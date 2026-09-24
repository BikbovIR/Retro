# -*- coding: utf-8 -*-
"""Единое окно результатов для Revit 2023 / pyRevit IronPython.

Положить этот файл рядом с script.py кнопки.
В начале script.py:
    from room_area_report import show_room_area_report

После завершения всех транзакций:
    show_room_area_report(
        completed_rooms, p_name_RetroArea,
        summary=summary, issues=issues, phase_name=phase.Name,
    )

ИЗМЕНЕНО [11] 24.09.2026: сводка -> список ошибок -> таблица помещений.
ИЗМЕНЕНО [12] 24.09.2026: отображение пустой таблицы и длинного списка ошибок.

Отчёт читает фактически записанный параметр, не изменяя модель.
Числа преобразуются из внутренних единиц Revit в м² только для отображения.
В обычной работе окно закрывается кнопкой ОК (также доступна с клавиатуры).

Основа: pyrevit.forms.WPFWindow, literal_string=True, handle_esc=False.
https://docs.pyrevitlabs.io/reference/pyrevit/forms/
"""

import clr

clr.AddReference("System.Data")
clr.AddReference("PresentationFramework")

from System import Array, Object
from System.Data import DataTable
from System.Windows import SystemParameters, Visibility
from Autodesk.Revit.DB import (
    BuiltInParameter, SpecTypeId, StorageType, UnitTypeId, UnitUtils,
)
from pyrevit import forms


_XAML = u"""
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Результаты расчёта площадей"
        Width="1000" Height="900"
        WindowStartupLocation="CenterOwner"
        WindowStyle="None" ResizeMode="NoResize"
        ShowInTaskbar="False" Topmost="True"
        FontFamily="Segoe UI" FontSize="14"
        Background="White" Foreground="#202B3A">
    <Window.Resources>
        <Style x:Key="NameText" TargetType="TextBlock">
            <Setter Property="TextWrapping" Value="Wrap"/>
            <Setter Property="Margin" Value="8,7"/>
        </Style>
        <Style x:Key="NumberText" TargetType="TextBlock">
            <Setter Property="TextAlignment" Value="Right"/>
            <Setter Property="Margin" Value="8,7"/>
        </Style>
        <Style x:Key="ColumnHeader" TargetType="DataGridColumnHeader">
            <Setter Property="Background" Value="#EDF1F6"/>
            <Setter Property="Foreground" Value="#202B3A"/>
            <Setter Property="FontWeight" Value="SemiBold"/>
            <Setter Property="Padding" Value="8,12"/>
            <Setter Property="HorizontalContentAlignment" Value="Stretch"/>
            <Setter Property="VerticalContentAlignment" Value="Center"/>
            <Setter Property="BorderBrush" Value="#D7DEE7"/>
            <Setter Property="BorderThickness" Value="0,0,1,1"/>
            <Setter Property="ContentTemplate">
                <Setter.Value>
                    <DataTemplate>
                        <TextBlock Text="{Binding}" TextWrapping="Wrap"/>
                    </DataTemplate>
                </Setter.Value>
            </Setter>
        </Style>
        <Style x:Key="RightHeader" TargetType="DataGridColumnHeader"
               BasedOn="{StaticResource ColumnHeader}">
            <Setter Property="ContentTemplate">
                <Setter.Value>
                    <DataTemplate>
                        <TextBlock Text="{Binding}" TextWrapping="Wrap"
                                   TextAlignment="Right"
                                   HorizontalAlignment="Stretch"/>
                    </DataTemplate>
                </Setter.Value>
            </Setter>
        </Style>
    </Window.Resources>
    <Border BorderBrush="#AEBAC8" BorderThickness="1" Padding="24">
        <Grid>
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="*"/>
                <RowDefinition Height="Auto"/>
            </Grid.RowDefinitions>

            <Border x:Name="drag_header" Grid.Row="0"
                    Background="Transparent" Padding="0,0,0,10">
                <StackPanel>
                    <TextBlock Text="Результаты расчёта площадей"
                               FontSize="23" FontWeight="SemiBold"/>
                    <TextBlock x:Name="phase_caption" Margin="0,5,0,0"
                               Foreground="#586579" TextWrapping="Wrap"/>
                </StackPanel>
            </Border>

            <!-- ИЗМЕНЕНО [11, 12]: общий порядок разделов и прокрутка
                 всего содержимого на небольшом экране. Кнопка ОК закреплена. -->
            <ScrollViewer Grid.Row="1" VerticalScrollBarVisibility="Auto"
                          HorizontalScrollBarVisibility="Disabled"
                          Padding="0,0,6,0">
                <StackPanel>
                    <Border Background="#F4F7FA" BorderBrush="#D7DEE7"
                            BorderThickness="1" Padding="12" Margin="0,0,0,14">
                        <StackPanel>
                            <TextBlock Text="Сводка" FontWeight="SemiBold"
                                       FontSize="16" Margin="0,0,0,6"/>
                            <TextBlock x:Name="summary_text" TextWrapping="Wrap"
                                       LineHeight="21"/>
                            <TextBlock x:Name="result_note_text" TextWrapping="Wrap"
                                       Foreground="#586579" Margin="0,8,0,0"/>
                        </StackPanel>
                    </Border>

                    <TextBlock x:Name="issues_heading" Text="Список ошибок"
                               FontSize="16" FontWeight="SemiBold" Margin="0,0,0,8"/>
                    <!-- Высота ограничена: длинный список не вытесняет таблицу.
                         Текст ошибок можно выделить и скопировать. -->
                    <TextBox x:Name="issues_text" IsReadOnly="True"
                             IsUndoEnabled="False" AcceptsReturn="True"
                             TextWrapping="Wrap" VerticalScrollBarVisibility="Auto"
                             HorizontalScrollBarVisibility="Disabled"
                             Height="140" Padding="10" Margin="0,0,0,16"
                             Background="#FAFBFD" BorderBrush="#D7DEE7"/>

                    <TextBlock Text="Отчёт помещений" FontSize="16"
                               FontWeight="SemiBold" Margin="0,0,0,5"/>
                    <TextBlock x:Name="parameter_caption"
                               Margin="0,0,0,10" Foreground="#586579"
                               TextWrapping="Wrap"/>

                    <DataGrid x:Name="rooms_grid" Height="280"
                              AutoGenerateColumns="False" IsReadOnly="True"
                              CanUserAddRows="False" CanUserDeleteRows="False"
                              CanUserReorderColumns="False" CanUserSortColumns="False"
                              HeadersVisibility="Column" GridLinesVisibility="All"
                              ColumnHeaderStyle="{StaticResource ColumnHeader}"
                              HorizontalGridLinesBrush="#E3E8EE"
                              VerticalGridLinesBrush="#D7DEE7"
                              BorderBrush="#D7DEE7" Background="White"
                              AlternatingRowBackground="#F7F9FC"
                              EnableRowVirtualization="True"
                              ScrollViewer.VerticalScrollBarVisibility="Auto"
                              ScrollViewer.HorizontalScrollBarVisibility="Auto">
                        <DataGrid.Columns>
                            <DataGridTextColumn Header="Имя помещения"
                                                Binding="{Binding RoomName}" Width="2.2*"
                                                ElementStyle="{StaticResource NameText}"/>
                            <DataGridTextColumn Header="ID помещения"
                                                Binding="{Binding RoomId}" Width="1*"
                                                HeaderStyle="{StaticResource RightHeader}"
                                                ElementStyle="{StaticResource NumberText}"/>
                            <DataGridTextColumn Header="Стандартная площадь, м²"
                                                Binding="{Binding StandardArea}" Width="1.6*"
                                                HeaderStyle="{StaticResource RightHeader}"
                                                ElementStyle="{StaticResource NumberText}"/>
                            <DataGridTextColumn Binding="{Binding NewArea}" Width="1.6*"
                                                HeaderStyle="{StaticResource RightHeader}"
                                                ElementStyle="{StaticResource NumberText}"/>
                        </DataGrid.Columns>
                    </DataGrid>

                    <TextBlock x:Name="empty_rooms_note"
                               Text="Нет помещений с подтверждённым результатом для отображения."
                               TextWrapping="Wrap" Foreground="#586579"
                               Margin="0,8,0,0"/>
                </StackPanel>
            </ScrollViewer>

            <DockPanel Grid.Row="2" Margin="0,18,0,0" LastChildFill="True">
                <Button x:Name="ok_button" DockPanel.Dock="Right"
                        Content="ОК" IsDefault="True"
                        Width="110" Height="38" Margin="18,0,0,0"/>
                <TextBlock x:Name="footer_text" VerticalAlignment="Center"
                           Foreground="#586579" TextWrapping="Wrap"/>
            </DockPanel>
        </Grid>
    </Border>
</Window>
"""


def _area_text(value):
    """Площадь в м² с двумя знаками после запятой."""
    square_metres = UnitUtils.ConvertFromInternalUnits(
        value, UnitTypeId.SquareMeters
    )
    return u"{:.2f}".format(square_metres).replace(".", ",")


def _parameter_text(parameter):
    if parameter is None:
        return u"Нет параметра"
    if parameter.StorageType != StorageType.Double:
        return u"Тип данных не «Площадь»"
    if not parameter.Definition.GetDataType().Equals(SpecTypeId.Area):
        return u"Тип данных не «Площадь»"
    if not parameter.HasValue:
        return u"Не заполнен"
    return _area_text(parameter.AsDouble())


def _make_table(rooms, parameter_name):
    table = DataTable("RoomAreas")
    # Строковые столбцы позволяют показывать состояние отсутствующего параметра.
    for column_name in ("RoomName", "RoomId", "StandardArea", "NewArea"):
        table.Columns.Add(column_name)

    for room in rooms:
        name_parameter = room.get_Parameter(BuiltInParameter.ROOM_NAME)
        room_name = name_parameter.AsString() if name_parameter is not None else None
        target_parameter = room.LookupParameter(parameter_name)
        values = [
            room_name or u"Без имени",
            str(room.Id.IntegerValue),
            _area_text(room.Area),
            _parameter_text(target_parameter),
        ]
        table.Rows.Add(Array[Object](values))

    return table


class _RoomAreaReportWindow(forms.WPFWindow):
    # ИЗМЕНЕНО [11]: сводка и ошибки передаются из основного скрипта.
    def __init__(self, table, parameter_name, summary=None, issues=None,
                 phase_name=None, result_note=None):
        self._confirmed = False
        forms.WPFWindow.__init__(
            self, _XAML, literal_string=True,
            handle_esc=False, set_owner=True,
        )

        # Ограничить размер доступной рабочей областью экрана.
        work_area = SystemParameters.WorkArea
        self.Width = min(1000.0, max(320.0, work_area.Width - 40.0))
        self.Height = min(900.0, max(320.0, work_area.Height - 40.0))

        # ИЗМЕНЕНО [11]: сверху сводка, затем полный нумерованный список ошибок.
        self.phase_caption.Text = u"Стадия расчёта: {}".format(phase_name or u"")
        self.phase_caption.Visibility = Visibility.Visible if phase_name else Visibility.Collapsed
        self.summary_text.Text = (summary if summary is not None else
                                  u"Помещений в отчёте: {}".format(table.Rows.Count))
        self.result_note_text.Text = result_note or u""
        self.result_note_text.Visibility = Visibility.Visible if result_note else Visibility.Collapsed

        issue_messages = list(issues or [])
        self.issues_heading.Text = u"Список ошибок ({})".format(len(issue_messages))
        self.issues_text.Text = (u"\n".join(
            u"{}. {}".format(index, message)
            for index, message in enumerate(issue_messages, 1)
        ) if issue_messages else u"Ошибок не обнаружено.")
        self.issues_text.Height = (min(150.0, max(70.0, self.Height * 0.17))
                                   if issue_messages else 42.0)

        self._table = table
        self.rooms_grid.ItemsSource = table.DefaultView
        # ИЗМЕНЕНО [12]: конечная высота сохраняет прокрутку и виртуализацию таблицы.
        self.rooms_grid.Height = (min(320.0, max(180.0, self.Height * 0.34))
                                  if table.Rows.Count else 80.0)
        self.empty_rooms_note.Visibility = (Visibility.Collapsed if table.Rows.Count
                                             else Visibility.Visible)
        self.rooms_grid.Columns[3].Header = u"{}, м²".format(parameter_name)
        self.parameter_caption.Text = (
            u"Параметр: {}. Показаны значения, записанные в модель."
            .format(parameter_name)
        )
        self.footer_text.Text = (
            u"Помещений: {}. Для продолжения работы нажмите ОК."
            .format(table.Rows.Count)
        )

        self.ok_button.Click += self._on_ok
        self.drag_header.MouseLeftButtonDown += self._on_drag
        self.Closing += self._on_closing

    def _on_ok(self, sender, args):
        self._confirmed = True
        self.Close()

    def _on_closing(self, sender, args):
        # В частности, запретить закрытие через Alt+F4 до подтверждения.
        if not self._confirmed:
            args.Cancel = True

    def _on_drag(self, sender, args):
        self.DragMove()


def show_room_area_report(rooms, parameter_name=u"RETRO_Площадь помещения",
                          summary=None, issues=None, phase_name=None, result_note=None):
    """Показать сводку, ошибки и таблицу после завершения всех транзакций.

    Args:
        rooms: коллекция DB.Architecture.Room из текущего проекта.
        parameter_name: имя параметра помещения с типом данных «Площадь».
        summary: готовый текст счётчиков основного скрипта.
        issues: список текстов ошибок без нумерации.
        phase_name: имя стадии расчёта.
        result_note: пояснение к неполному или пустому результату.

    Метод возвращается после подтверждения ОК. Модель не изменяется.
    ИЗМЕНЕНО [11]: прежний вызов с двумя аргументами также поддерживается.
    """
    table = _make_table(rooms, parameter_name)
    window = _RoomAreaReportWindow(
        table, parameter_name, summary=summary, issues=issues,
        phase_name=phase_name, result_note=result_note,
    )
    window.ShowDialog()
