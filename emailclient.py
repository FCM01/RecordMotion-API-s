
from logging import exception
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
class email():
    def send_welcome(self,reciever,type):
        try:
            message = Mail(
            from_email='info.recordmotion@gmail.com',
            to_emails='faraimatyukira1@gmail.com',
            subject='Welcome to RecordMotion',
            html_content=' <div ><table><tr><th>Welcome To RecordMotion</th></tr><tr><td><img src=" http://cdn.mcauto-images-production.sendgrid.net/1c6b22743e8249aa/d770c5a3-ce32-4f9e-a0f0-18791192fd00/1500x1500.png" alt="Girl in a jacket" width="400" height="350"></td><td>ReordMotion is a new way to look at EHR systems and move from paper to electronic records. With the aim of assisting small to medium size clinics and private doctors in managing patients and their day-to-day operations</td></tr></table></div><div data-role="module-unsubscribe" class="module" role="module" data-type="unsubscribe" style="color:#444444; font-size:12px; line-height:20px; padding:16px 16px 16px 16px; text-align:Center;" data-muid="4e838cf3-9892-4a6d-94d6-170e474d21e5"><div class="Unsubscribe--addressLine"><p class="Unsubscribe--senderName"style="font-size:12px;line-height:20px">{{Sender_Name}}</p><p style="font-size:12px;line-height:20px"><span class="Unsubscribe--senderAddress">{{Sender_Address}}</span>, <span class="Unsubscribe--senderCity">{{Sender_City}}</span>, <span class="Unsubscribe--senderState">{{Sender_State}}</span> <span class="Unsubscribe--senderZip">{{Sender_Zip}}</span></p></div><p style="font-size:12px; line-height:20px;"><a class="Unsubscribe--unsubscribeLink" href="{{{unsubscribe}}}" target="_blank" style="font-family:sans-serif;text-decoration:none;">Unsubscribe</a>-<a href="{{{unsubscribe_preferences}}}" target="_blank" class="Unsubscribe--unsubscribePreferences" style="font-family:sans-serif;text-decoration:none;">Unsubscribe Preferences</a></p></div>')

            SENDGRID_API_KEY=""
            try:
                sg = SendGridAPIClient(SENDGRID_API_KEY)
                print(sg)
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)
        except Exception as e :
            print("ERROR=email:send_perscription()-->",e)

    def send_perscription(self,reciever,type):
        try:
            message = Mail(
            from_email='info.recordmotion@gmail.com',
            to_emails='faraimatyukira1@gmail.com',
            subject='Welcome to RecordMotion',
            html_content=' <div ><table><tr><th>Welcome To RecordMotion</th></tr><tr><td><img src=" http://cdn.mcauto-images-production.sendgrid.net/1c6b22743e8249aa/d770c5a3-ce32-4f9e-a0f0-18791192fd00/1500x1500.png" alt="Girl in a jacket" width="400" height="350"></td><td>ReordMotion is a new way to look at EHR systems and move from paper to electronic records. With the aim of assisting small to medium size clinics and private doctors in managing patients and their day-to-day operations</td></tr></table></div><div data-role="module-unsubscribe" class="module" role="module" data-type="unsubscribe" style="color:#444444; font-size:12px; line-height:20px; padding:16px 16px 16px 16px; text-align:Center;" data-muid="4e838cf3-9892-4a6d-94d6-170e474d21e5"><div class="Unsubscribe--addressLine"><p class="Unsubscribe--senderName"style="font-size:12px;line-height:20px">{{Sender_Name}}</p><p style="font-size:12px;line-height:20px"><span class="Unsubscribe--senderAddress">{{Sender_Address}}</span>, <span class="Unsubscribe--senderCity">{{Sender_City}}</span>, <span class="Unsubscribe--senderState">{{Sender_State}}</span> <span class="Unsubscribe--senderZip">{{Sender_Zip}}</span></p></div><p style="font-size:12px; line-height:20px;"><a class="Unsubscribe--unsubscribeLink" href="{{{unsubscribe}}}" target="_blank" style="font-family:sans-serif;text-decoration:none;">Unsubscribe</a>-<a href="{{{unsubscribe_preferences}}}" target="_blank" class="Unsubscribe--unsubscribePreferences" style="font-family:sans-serif;text-decoration:none;">Unsubscribe Preferences</a></p></div>')
            with open('attachment.pdf', 'rb') as f:
                data = f.read()
                f.close()
            encoded_file = base64.b64encode(data).decode()

            attachedFile = Attachment(
                FileContent(encoded_file),
                FileName('attachment.pdf'),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            message.attachment = attachedFile
            SENDGRID_API_KEY=''
            try:
                sg = SendGridAPIClient(SENDGRID_API_KEY)
                print(sg)
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)

        except Exception as e :
            print("ERROR=email:send_perscription()-->",e)


message = Mail(
    from_email='info.recordmotion@gmail.com',
    to_emails='faraimatyukira1@gmail.com',
    subject='Welcome to RecordMotion',
    html_content=' <div ><table><tr><th>Welcome To RecordMotion</th></tr><tr><td><img src=" http://cdn.mcauto-images-production.sendgrid.net/1c6b22743e8249aa/d770c5a3-ce32-4f9e-a0f0-18791192fd00/1500x1500.png" alt="Girl in a jacket" width="400" height="350"></td><td>ReordMotion is a new way to look at EHR systems and move from paper to electronic records. With the aim of assisting small to medium size clinics and private doctors in managing patients and their day-to-day operations</td></tr></table></div><div data-role="module-unsubscribe" class="module" role="module" data-type="unsubscribe" style="color:#444444; font-size:12px; line-height:20px; padding:16px 16px 16px 16px; text-align:Center;" data-muid="4e838cf3-9892-4a6d-94d6-170e474d21e5"><div class="Unsubscribe--addressLine"><p class="Unsubscribe--senderName"style="font-size:12px;line-height:20px">{{Sender_Name}}</p><p style="font-size:12px;line-height:20px"><span class="Unsubscribe--senderAddress">{{Sender_Address}}</span>, <span class="Unsubscribe--senderCity">{{Sender_City}}</span>, <span class="Unsubscribe--senderState">{{Sender_State}}</span> <span class="Unsubscribe--senderZip">{{Sender_Zip}}</span></p></div><p style="font-size:12px; line-height:20px;"><a class="Unsubscribe--unsubscribeLink" href="{{{unsubscribe}}}" target="_blank" style="font-family:sans-serif;text-decoration:none;">Unsubscribe</a>-<a href="{{{unsubscribe_preferences}}}" target="_blank" class="Unsubscribe--unsubscribePreferences" style="font-family:sans-serif;text-decoration:none;">Unsubscribe Preferences</a></p></div>')

SENDGRID_API_KEY=""
try:
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    print(sg)
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e)

