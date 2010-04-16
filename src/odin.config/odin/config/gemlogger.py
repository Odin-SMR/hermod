from time import time

def timer(f):
    def wrapper(*arg):
        t1 = time()
        res = f(*arg)
        t2 = time()
        print '%s took %0.1f s' % (f.func_name, (t2-t1))
        return res
    return wrapper

def logger(f):
    name = f.func_name
    def wrapped(*args, **kwargs):
        self = args[0]
        if hasattr(self,'logfile'):
            self.logfile.write( "Calling: %s %s %s\n" % (name, 
                repr(args[1:]), 
                repr(kwargs)
                ))
        result = f(*args,**kwargs)
        if hasattr(self,'logfile'):
            self.logfile.write("Called: %s %s %s returned: %s\n" % (repr(name), 
                repr(args[1:]), 
                repr(kwargs), 
                repr(result)
                ))
        return result
    wrapped.__doc__ = f.__doc__
    return wrapped
