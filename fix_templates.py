import re
from pathlib import Path

# Fix admin_dashboard.html
p1 = Path('templates/dashboard/admin_dashboard.html')
if p1.exists():
    c1 = p1.read_text(encoding='utf-8')
    c1 = re.sub(r'dept\.hod\.id==h\.id', 'dept.hod.id == h.id', c1)
    c1 = re.sub(r'endif\s*\r?\n\s*\%\}', 'endif %}', c1)
    p1.write_text(c1, encoding='utf-8')

# Fix manage_students.html
p2 = Path('templates/dashboard/manage_students.html')
if p2.exists():
    c2 = p2.read_text(encoding='utf-8')
    c2 = c2.replace("status_filter=='Safe'", "status_filter == 'Safe'")
    c2 = c2.replace("status_filter=='Shortage'", "status_filter == 'Shortage'")
    p2.write_text(c2, encoding='utf-8')

# Fix student_detail.html
p3 = Path('templates/dashboard/student_detail.html')
if p3.exists():
    c3 = p3.read_text(encoding='utf-8')
    c3 = re.sub(r'\{\%\s*\r?\n\s*endblock\s*\%\}', '{% endblock %}', c3)
    p3.write_text(c3, encoding='utf-8')

print('Regex replacements complete.')
