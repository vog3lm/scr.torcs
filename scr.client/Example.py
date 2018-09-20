name = 'example-driver'
angles = ['-90','-75','-60','-45','-30','-20','-15','-10','-5','0','5','10','15','20','30','45','60','75','90']

def drive(sensors):
	return {'accel':0.1
           ,'brake':0
           ,'steer':0
           ,'gear':1
           ,'clutch':0
           ,'focus':0.0
           ,'meta':0}