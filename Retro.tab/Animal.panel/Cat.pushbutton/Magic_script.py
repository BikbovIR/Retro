__title__ = "Cat"

__doc__   = """
It's just a cat
"""


from pyrevit           import script
output = script.get_output()

html_code = '''<div style="width:200px;height:200px;background:url('https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif') center/cover no-repeat;animation:shake 0.5s infinite;transform-origin:center;">
<style>
@keyframes shake {
  0% { transform: rotate(0deg); }
  25% { transform: rotate(5deg); }
  50% { transform: rotate(0deg); }
  75% { transform: rotate(-5deg); }
  100% { transform: rotate(0deg); }
}
</style>
</div>'''
output.print_html(html_code)