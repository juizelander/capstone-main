import re

with open(r'c:\Users\Justin Lorenz\Downloads\capstone-main\accounts\templates\accounts\landing_page.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CSS
css_old = """
        /* --- Student News Section --- */
        .student-news-section {
            padding: 80px 5%;
            background-color: #f8fafc;
        }

        .news-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .news-featured {
            height: 100%;
        }

        .news-side {
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        .news-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex;
            flex-direction: column;
            border: 1px solid #e2e8f0;
        }

        .news-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }

        .news-img {
            width: 100%;
            background-size: cover;
            background-position: center;
        }

        .news-featured .news-img {
            height: 350px;
        }

        .news-side .news-img {
            height: 150px;
        }

        .news-body {
            padding: 25px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .news-side .news-body {
            padding: 20px;
        }

        .news-body h3 {
            color: #1e293b;
            font-size: 1.4rem;
            margin-bottom: 15px;
            line-height: 1.3;
            font-family: 'Raleway', sans-serif;
            font-weight: 700;
        }

        .news-side .news-body h3 {
            font-size: 1.1rem;
            margin-bottom: 10px;
        }

        .news-meta {
            margin-top: auto;
            color: #94a3b8;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        .news-side .news-card {
            cursor: pointer;
            margin-bottom: 15px;
        }

        .news-side .news-content {
            display: none;
            color: #475569;
            font-size: 0.95rem;
            line-height: 1.6;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px dashed #e2e8f0;
        }

        .news-side .news-card.expanded .news-content {
            display: block;
        }

        .news-side .news-card.expanded {
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border-color: #bee3f8;
            background: #f8fafc;
        }

        .news-side .expand-icon {
            transition: transform 0.3s ease;
            color: #94a3b8;
        }

        .news-side .news-card.expanded .expand-icon {
            transform: rotate(180deg);
        }

        @media (max-width: 992px) {
            .news-grid {
                grid-template-columns: 1fr;
            }

            .news-featured .news-img {
                height: 250px;
            }
        }
"""

css_new = """
        /* --- Student News Section --- */
        .student-news-section {
            padding: 80px 5%;
            background-color: #f8fafc;
        }

        .news-scroll-container {
            display: flex;
            overflow-x: auto;
            gap: 25px;
            padding: 10px 20px 30px;
            max-width: 1200px;
            margin: 0 auto;
            scroll-snap-type: x mandatory;
        }

        /* Custom Scrollbar for news */
        .news-scroll-container::-webkit-scrollbar {
            height: 8px;
        }
        .news-scroll-container::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
        }
        .news-scroll-container::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }
        .news-scroll-container::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }

        .news-card-horizontal {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex;
            flex-direction: column;
            border: 1px solid #e2e8f0;
            min-width: 320px;
            width: 320px;
            flex: 0 0 auto;
            scroll-snap-align: start;
            cursor: pointer;
        }

        .news-card-horizontal:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }

        .news-card-horizontal .news-img {
            width: 100%;
            height: 180px;
            background-size: cover;
            background-position: center;
        }

        .news-card-horizontal .news-body {
            padding: 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .news-card-horizontal h3 {
            color: #1e293b;
            font-size: 1.2rem;
            margin-bottom: 10px;
            line-height: 1.3;
            font-family: 'Raleway', sans-serif;
            font-weight: 700;
        }

        .news-card-horizontal p {
            color: #475569;
            font-size: 0.95rem;
            line-height: 1.5;
            flex: 1;
            margin-bottom: 15px;
        }

        .news-card-horizontal .news-meta {
            color: #94a3b8;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-top: auto;
        }
"""
content = content.replace(css_old.strip(), css_new.strip())

# 2. Extract sections
# Hero
hero_match = re.search(r'(<section class="landing-hero">.*?</section>)', content, re.DOTALL)
hero_html = hero_match.group(1)

# Modify hero style to fit new spot
hero_html_new = hero_html.replace('<section class="landing-hero">', '<section class="landing-hero" style="margin-top: 40px; min-height: 70vh; padding: 120px 40px 60px;">')

# Features
features_match = re.search(r'(<section id="features" class="features-section">.*?</section>)', content, re.DOTALL)
features_html = features_match.group(1)

# Featured Programs
fp_match = re.search(r'(<section id="featured-programs" class="featured-programs-section">.*?</section>)', content, re.DOTALL)
fp_html = fp_match.group(1)

# Applicant News (need to rewrite its current HTML completely anyway)
news_html_new = """
        <!-- Student News Section (Horizontal Scroll) -->
        <section class="student-news-section">
            <h2 class="section-heading" style="text-align: center; margin-bottom: 30px;">Applicant News</h2>

            {% if announcements %}
            <div class="news-scroll-container">
                {% for item in announcements %}
                <div class="news-card-horizontal" onclick="toggleNewsModal(this)" data-title="{{ item.title|escapejs }}" data-content="{{ item.content|escapejs }}" data-date="{{ item.created_at|date:'F d, Y' }}" data-image="{% if item.image %}{{ item.image.url }}{% else %}/static/accounts/scholarsync_logo.png{% endif %}">
                    <div class="news-img"
                        style="background-image: url('{% if item.image %}{{ item.image.url }}{% else %}/static/accounts/scholarsync_logo.png{% endif %}');">
                    </div>
                    <div class="news-body">
                        <h3>{{ item.title|truncatechars:45 }}</h3>
                        <p>{{ item.content|truncatechars:80 }}</p>
                        <div class="news-meta">
                            {{ item.created_at|date:"F d, Y" }}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>

            <!-- News Modal Overlay for viewing details -->
            <div id="newsDetailModal" class="news-modal" style="display:none; position:fixed; z-index:100000; left:0; top:0; width:100%; height:100%; background-color:rgba(0,0,0,0.6); align-items:center; justify-content:center;">
                <div class="news-modal-content" style="background:#fff; width:90%; max-width:600px; border-radius:15px; overflow:hidden; position:relative; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                    <span class="news-close-btn" onclick="closeNewsModal()" style="position:absolute; top:15px; right:20px; font-size:1.5rem; cursor:pointer; color:#333; background:rgba(255,255,255,0.8); border-radius:50%; width:35px; height:35px; display:flex; align-items:center; justify-content:center; z-index:2;">&times;</span>
                    <div id="newsModalImage" style="width:100%; height:250px; background-size:cover; background-position:center;"></div>
                    <div style="padding:25px;">
                        <h3 id="newsModalTitle" style="margin-bottom:10px; color:#1e293b; font-size:1.5rem;"></h3>
                        <div id="newsModalDate" style="color:#94a3b8; font-size:0.85rem; margin-bottom:20px; font-weight:600;"></div>
                        <p id="newsModalText" style="color:#475569; line-height:1.6; white-space:pre-wrap; max-height:250px; overflow-y:auto;"></p>
                    </div>
                </div>
            </div>

            <script>
                function toggleNewsModal(card) {
                    document.getElementById('newsModalTitle').innerText = card.getAttribute('data-title');
                    document.getElementById('newsModalText').innerText = card.getAttribute('data-content');
                    document.getElementById('newsModalDate').innerText = card.getAttribute('data-date');
                    document.getElementById('newsModalImage').style.backgroundImage = "url('" + card.getAttribute('data-image') + "')";
                    document.getElementById('newsDetailModal').style.display = 'flex';
                }
                function closeNewsModal() {
                    document.getElementById('newsDetailModal').style.display = 'none';
                }
                // Close modal on click outside
                window.addEventListener('click', function(event) {
                    var modal = document.getElementById('newsDetailModal');
                    if (event.target == modal) {
                        modal.style.display = 'none';
                    }
                });
            </script>
            {% else %}
            <!-- Fallback if no news -->
            <div
                style="text-align: center; color: #94a3b8; padding: 40px; border: 2px dashed #e2e8f0; border-radius: 20px; max-width: 800px; margin: 0 auto;">
                <i class="fa-solid fa-newspaper" style="font-size: 3rem; margin-bottom: 20px;"></i>
                <h3>No Recent News</h3>
                <p>Check back later for important announcements and scholarship guides!</p>
            </div>
            {% endif %}
        </section>
"""

# 3. Build new container body
new_container_body = f"""
    <div class="landing-container">
{fp_html}

{news_html_new}

{hero_html_new}

{features_html}
"""

all_content_matcher = r'(<div class="landing-container">.*?)(<footer class="premium-footer">)'
content = re.sub(all_content_matcher, new_container_body + r'\n        \2', content, flags=re.DOTALL)

with open(r'c:\Users\Justin Lorenz\Downloads\capstone-main\accounts\templates\accounts\landing_page.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Landing page successfully updated with reordered sections and horizontal news scroll.")
