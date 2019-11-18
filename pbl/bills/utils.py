


def send_bill_email(emailfrom,emailto,name,url):
    try:
        msg = Message('Bill Copy',
                    sender=emailfrom,
                    recipients=[emailto])
        msg.body = f'''Thanks for shopping at {name}
        You can view your bill by following the link given below:
        {url}
        If you did not make this request then simply ignore this email and no changes will be made.
    '''
        mail.send(msg)
    except :
        flash('unable to send mail','danger')
