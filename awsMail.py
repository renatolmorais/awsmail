import sys,os
import boto3
from botocore.exceptions import ClientError
import argparse
from configparser import ConfigParser as cp, ExtendedInterpolation as ei

# NECESSARIO INSERIR O REMETENTE NA VARIAVEL ABAIXO
sender = ''
label = 'AWS SDK for Python (Boto)'
footer = 'AWS SDK for Python (Boto)'

def sendmail(rctp,subject,message):

	global sender
	global label
	global footer
	# Replace sender@example.com with your "From" address.
	# This address must be verified with Amazon SES.
	SENDER = sender
	
	# Replace recipient@example.com with a "To" address. If your account 
	# is still in the sandbox, this address must be verified.
	RECIPIENT = rctp
	
	# Specify a configuration set. If you do not want to use a configuration
	# set, comment the following variable, and the 
	# ConfigurationSetName=CONFIGURATION_SET argument below.
	#CONFIGURATION_SET = "ConfigSet"
	
	# If necessary, replace sa-east-1 with the AWS Region you're using for Amazon SES.
	AWS_REGION = "sa-east-1"
	
	# The subject line for the email.
	SUBJECT = subject
	html_message = message
	
	if type(message) is list:
		message = '\n'.join(message)
		html_message = '<br>'.join(html_message)
	# The email body for recipients with non-HTML email clients.
	BODY_TEXT = ('''{label}\r\n{message}\r\n{footer}.'''.format(label=label,message=message,footer=footer))
	            
	# The HTML body of the email.
	BODY_HTML = '''<html>
	<head><title>{label}</title></head>
	<body>
	  <h3>{label}</h3>
	  <p>{message}</p>
	  <h3>{footer}</h3>
	</body>
	</html>
	'''.format(label=label,message=html_message,footer=footer)            
	
	# The character encoding for the email.
	CHARSET = "UTF-8"
	
	# Create a new SES resource and specify a region.
	client = boto3.client('ses',region_name=AWS_REGION)
	
	# Try to send the email.
	try:
	    #Provide the contents of the email.
	    response = client.send_email(
	        Destination={
	            'ToAddresses': [
	                RECIPIENT,
	            ],
	        },
	        Message={
	            'Body': {
	                'Html': {
	                    'Charset': CHARSET,
	                    'Data': BODY_HTML,
	                },
	                'Text': {
	                    'Charset': CHARSET,
	                    'Data': BODY_TEXT,
	                },
	            },
	            'Subject': {
	                'Charset': CHARSET,
	                'Data': SUBJECT,
	            },
	        },
	        Source=SENDER,
	        # If you are not using a configuration set, comment or delete the
	        # following line
	        #ConfigurationSetName=CONFIGURATION_SET,
	    )
	# Display an error if something goes wrong.	
	except ClientError as e:
	    print(e.response['Error']['Message'])
	else:
	    print("Email sent! Message ID:"),
	    print(response['MessageId'])

if __name__ == '__main__':
	#sendmail('renatolmorais@gmail.com','teste','ola')
	ap = argparse.ArgumentParser(
		description='Enviar e-mails pela AWS',
		usage='{prog} [-h] -d -s "MESSAGE"'.format(prog=sys.argv[0]),
	)

	ap.add_argument(
		'-d',
		required=True,
		help='destinatario que recebera a mensagem',
		metavar='destinatario',
		dest='rctp',
		)
		
	ap.add_argument(
		'-s',
		required=False,
		help="assunto da mensagem",
		dest='subject',
		)

	ap.add_argument(
                '-c',
                required=False,
                help="arquivo de configuracao",
                dest='configfile',
                )

	ap.add_argument(
		"message",
		help="mensagen que sera enviada ao destinatario ou um arquivo de texto",
		metavar='MESSAGE',
		)

	args = vars(ap.parse_args())

	configfile = args['configfile'] if args['configfile'] else ''

	if os.path.exists(configfile):
		config = cp(interpolation=ei())
		config.read(configfile)
		sender = config.get('global','sender')
		label = config.get('global','label')
		footer = config.get('global','footer')

	rctp = args['rctp']
	subject = args['subject'] if args['subject'] else 'Sem assunto'
	message = args['message']
	if os.path.exists(message):
		with open(message,'r') as fp:
			message = fp.readlines()
	sendmail(rctp,subject,message)
