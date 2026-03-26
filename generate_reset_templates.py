import os

template_dir = r"c:\Users\Justin Lorenz\Downloads\capstone-main\accounts\templates\accounts"

base_top = """<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Password Reset - Student Management System</title>
  {% load static %}
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,100..900;1,100..900&family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
  <link rel="icon" type="image/png" href="{% static 'accounts/favicon.png' %}">
  <link rel="stylesheet" href="{% static 'accounts/style.css' %}">
</head>

<body>
  <div class="back-nav">
    <a href="{% url 'accounts:login' %}" class="back-btn">
      <i class="fas fa-arrow-left"></i> Back to Login
    </a>
  </div>
  <div class="auth-container">
    <div class="auth-header">
      <h1>ScholarSync <br>Subic</h1>
"""

base_bottom = """
  </div>
  <style>
    body {
      overflow: hidden;
    }
    .back-nav {
      position: absolute;
      top: 20px;
      left: 20px;
    }
    .back-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 20px;
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(10px);
      border-radius: 50px;
      text-decoration: none;
      color: #10B981;
      font-weight: 600;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
    }
    .back-btn:hover {
      transform: translateX(-5px);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
      background: white;
    }
  </style>
</body>
</html>
"""

# 1. form
form_html = base_top + """      <p>Reset your password</p>
    </div>
    
    {% if form.errors %}
    <div class="error-message">
      Please correct the errors below.
      {{ form.email.errors }}
    </div>
    {% endif %}

    <p style="text-align: center; color: #4b5563; margin-bottom: 20px; font-size: 0.95rem;">
        Enter your email address and we will send you a link to reset your password.
    </p>

    <form method="POST" class="auth-form">
      {% csrf_token %}
      <div class="input-group">
        <label for="id_email">Email address</label>
        <input type="email" name="email" id="id_email" placeholder="Enter your registered email" required>
      </div>
      <button type="submit" class="auth-button">Send Reset Link</button>
    </form>
""" + base_bottom

# 2. done
done_html = base_top + """      <p>Email Sent</p>
    </div>
    
    <div style="text-align: center; padding: 20px 0;">
        <i class="fa-solid fa-paper-plane" style="font-size: 3rem; color: #10B981; margin-bottom: 20px;"></i>
        <h3 style="color: #1f2937; margin-bottom: 15px; font-family: 'Raleway', sans-serif;">Check your inbox</h3>
        <p style="color: #4b5563; line-height: 1.6; font-size: 0.95rem;">
            We've emailed you instructions for setting your password. If an account exists with the email you entered, you should receive them shortly.
        </p>
        <p style="color: #6b7280; font-size: 0.85rem; margin-top: 20px;">
            If you don't receive an email, please make sure you've entered the address you registered with, and check your spam folder.
        </p>
    </div>
""" + base_bottom

# 3. confirm
confirm_html = base_top + """      <p>Set a new password</p>
    </div>
    
    {% if validlink %}
        {% if form.errors %}
        <div class="error-message">
            Please correct the errors below to change your password.
            {{ form.non_field_errors }}
        </div>
        {% endif %}

        <form method="POST" class="auth-form">
            {% csrf_token %}
            
            {% for field in form %}
            <div class="input-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {{ field }}
                {% if field.help_text %}
                <small style="color: #6b7280; font-size: 0.75rem; display: block; margin-top: 5px;">{{ field.help_text|safe }}</small>
                {% endif %}
                {% if field.errors %}
                <p style="color: #ef4444; font-size: 0.8rem; margin-top: 5px;">{{ field.errors.0 }}</p>
                {% endif %}
            </div>
            {% endfor %}

            <button type="submit" class="auth-button">Change Password</button>
        </form>
    {% else %}
        <div style="text-align: center; padding: 20px 0;">
            <i class="fa-solid fa-circle-xmark" style="font-size: 3rem; color: #ef4444; margin-bottom: 20px;"></i>
            <h3 style="color: #1f2937; margin-bottom: 15px; font-family: 'Raleway', sans-serif;">Link Expired or Invalid</h3>
            <p style="color: #4b5563; line-height: 1.6; font-size: 0.95rem;">
                The password reset link was invalid, possibly because it has already been used or expired. Please request a new password reset.
            </p>
            <a href="{% url 'accounts:password_reset' %}" class="auth-button" style="text-align: center; display: block; margin-top: 20px; text-decoration: none;">Request new link</a>
        </div>
    {% endif %}
""" + base_bottom

# 4. complete
complete_html = base_top + """      <p>Password Reset Complete</p>
    </div>
    
    <div style="text-align: center; padding: 20px 0;">
        <i class="fa-solid fa-circle-check" style="font-size: 3rem; color: #10B981; margin-bottom: 20px;"></i>
        <h3 style="color: #1f2937; margin-bottom: 15px; font-family: 'Raleway', sans-serif;">Password Updated!</h3>
        <p style="color: #4b5563; line-height: 1.6; font-size: 0.95rem;">
            Your password has been successfully set. You may go ahead and log in now.
        </p>
        <a href="{% url 'accounts:login' %}" class="auth-button" style="text-align: center; display: block; margin-top: 20px; text-decoration: none;">Log In</a>
    </div>
""" + base_bottom

# 5. Email Templates
email_subject = "Password Reset Request - ScholarSync Subic"
email_body = """You're receiving this email because you requested a password reset for your ScholarSync Subic account at {{ site_name }}.

Please go to the following page and choose a new password:
{{ protocol }}://{{ domain }}{% url 'accounts:password_reset_confirm' uidb64=uid token=token %}

Your username, in case you've forgotten: {{ user.get_username }}

If you didn't request this password reset, please ignore this email.

Thanks for using ScholarSync Subic!"""

email_html = """<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; padding: 20px;">
    <h2 style="color: #10B981;">ScholarSync Subic</h2>
    <p>Hi {{ user.get_username }},</p>
    <p>You requested a password reset for your ScholarSync Subic account.</p>
    <p>Click the button below to set a new password:</p>
    <p style="margin: 30px 0;">
        <a href="{{ protocol }}://{{ domain }}{% url 'accounts:password_reset_confirm' uidb64=uid token=token %}" style="background-color: #10B981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a>
    </p>
    <p>If you didn't request this action, you can safely ignore this email.</p>
    <br>
    <p>Thanks,<br>The ScholarSync team</p>
</body>
</html>"""

# Write files
with open(os.path.join(template_dir, 'password_reset_form.html'), 'w') as f: f.write(form_html)
with open(os.path.join(template_dir, 'password_reset_done.html'), 'w') as f: f.write(done_html)
with open(os.path.join(template_dir, 'password_reset_confirm.html'), 'w') as f: f.write(confirm_html)
with open(os.path.join(template_dir, 'password_reset_complete.html'), 'w') as f: f.write(complete_html)
with open(os.path.join(template_dir, 'password_reset_email.html'), 'w') as f: f.write(email_html)
with open(os.path.join(template_dir, 'password_reset_subject.txt'), 'w') as f: f.write(email_subject)

print("Generated password reset templates.")
