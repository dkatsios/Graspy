import os
def send_mail(recipient_mail, subject, message, attachment):
    outputs = []
    sep = os.sep
    cwd = os.path.dirname(os.path.abspath(__file__))
    if (attachment == 'None'): 
        os.system('echo "' + message + ' "| mail -s " ' + subject + ' " ' + recipient_mail)
    else:
        os.system("mpack -s " + subject + ' ' + cwd+sep+'files'+sep+attachment +  " " + recipient_mail)

    return outputs
