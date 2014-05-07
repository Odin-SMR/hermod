class IKerberosTicket:
    """
    renew a ticket
    check for valid ticket
    request a ticket
    """

    def request(self):
        """Request a ticket.

        Send a request to the KDC for a tgt
        return True if ticket recieved - False otherwise
        """
        raise NotImplementedError,"Implement the request method"

    def check(self):
        """Check for a valid ticket.

        Check the local cache for a valid ticket.
        return True if a ticket is found and valid, False othervise.
        """
        raise NotImplementedError,"Implement the check method"

    def renew(self):
        """Renew a ticket.

        Renew a valid ticket.
        return True if sucessful, False othervise.
        """
        raise NotImplementedError,"Implement the renew method"

class IGetFiles:
    """
    create a connection
    cp files
    close connection
    """

    def connect(self):
        """Connect to a service.

        Connect to a service that can deliver files.
        return True if sucsessful False othervise.
        """
        raise NotImplementedError,"Implement the connect method"

    def get(self,source,target):
        """Get file from connection.

        Copy file from source (remote) to target (local).
        return True if sucsessful False othervise.
        """
        raise NotImplementedError,"Implement the cp method"

    def put(self,source,target):
        """Get file to connection.

        Copy file from  source (local)  target (remote).
        return True if sucsessful False othervise.
        """
        raise NotImplementedError,"Implement the cp method"

    def close(self):
        """Close service.

        Dismount connection.
        return True if sucsessful False othervise.
        """
        raise NotImplementedError,"Implement the close method"

class IMatlab:
    """Opens a matlab session ready to run calculations
    """
    def start_matlab(self):
        """Start a session
        """
        raise NotImplementedError,"Implement the start_matlab method"

    def close_matlab(self):
        """Close session
        """
        raise NotImplementedError,"Implement the close_matlab method"

    def matlab_is_open(self):
        """test if still available
        """
        raise NotImplementedError,"Implement the matlab_is_open method"

    def matlab_command(self,command):
        """Put a command into matlab.
        """
        raise NotImplementedError,"Implement the matlab_command_is_open method"



class IMakeZPT:
    """ZPT-file generation.
    Needs a id-attribute to operate on 
    """
    def checkIfValid(self):
        """Check if we have a valid ZPT-file.

        If so return True ow. False
        """
        raise NotImplementedError,"Implement the checkIfValid method"

    def makeZPT(self):
        """Generate the specific
        return zpt-file as a string if successful None
        """
        raise NotImplementedError,"Implement the makeZPT method"

class IPbs:
    """send a job to cluster.
    """
    def submit(self):
        """Return True if submit was sucessfull
        """
        raise NotImplementedError,"Implement the submit method"
