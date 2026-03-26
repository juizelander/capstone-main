import os

filepath = r'c:\Users\Justin Lorenz\Downloads\capstone-main\accounts\templates\accounts\admin_dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the opening divs I added
content = content.replace('<div class="max-w-6xl mx-auto w-full">\n', '')

# Remove the extra closing divs I added
replacements = [
    (
        '            </div>\n          </div>\n          </div>\n        </div>\n\n        <!-- Student Applications Tab -->',
        '            </div>\n          </div>\n        </div>\n\n        <!-- Student Applications Tab -->'
    ),
    (
        '            </div>\n          </div>\n          </div>\n        </div>\n\n        <!-- Announcements Tab -->',
        '            </div>\n          </div>\n        </div>\n\n        <!-- Announcements Tab -->'
    ),
    (
        '            </div>\n          </div>\n          </div>\n        </div>\n\n        <!-- Students Tab -->',
        '            </div>\n          </div>\n        </div>\n\n        <!-- Students Tab -->'
    ),
    (
        '            </div>\n          </div>\n          </div>\n        </div>\n\n        <!-- Admins Tab -->',
        '            </div>\n          </div>\n        </div>\n\n        <!-- Admins Tab -->'
    ),
    (
        '            </div>\n          </div>\n          </div>\n        </div>\n    </div>\n  </div>',
        '            </div>\n          </div>\n        </div>\n    </div>\n  </div>'
    )
]

for old, new in replacements:
    content = content.replace(old, new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("File restored successfully.")
