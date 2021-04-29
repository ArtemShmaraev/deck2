import smtplib
import email.message


def send_msg(emai, code):
    msg = email.message.Message()
    msg['Subject'] = 'Код подтверждения'
    password = "321890artem"
    msg['From'] = "cinema4512@gmail.com"
    msg['To'] = emai
    msg.add_header('Content-Type', 'text/html')
    f = open("tools/email.txt", "r", encoding="utf-8")
    data = f.read()
    f.close()
    dat = data.replace("!№№!", str(code))
    msg.set_payload(dat)
    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    # Login Credentials for sending the mail
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))