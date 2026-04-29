import smtplib
from email.mime.text import MIMEText

msg = MIMEText('测试邮件', 'plain', 'utf-8')
msg['From'] = '2324903027@qq.com'
msg['To'] = '2324903027@qq.com'
msg['Subject'] = '测试'

with smtplib.SMTP_SSL('smtp.qq.com', 465) as s:
    s.login('2324903027@qq.com', 'sktjebqtzdjqdifi')
    s.sendmail('2324903027@qq.com', '2324903027@qq.com', msg.as_string())

print('发送成功')
