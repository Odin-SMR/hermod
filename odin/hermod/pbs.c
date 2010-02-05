#include <Python.h>
#include <structmember.h>
#include <pbs_error.h>
#include <pbs_ifl.h>
#include <stdio.h>

typedef struct 
{
    PyObject_HEAD
    int connection;
    PyObject * server;    
} TorqueConnection;

static PyObject * TorqueConnection_new(PyTypeObject *type, PyObject *args, PyObject * kwds)
{
    TorqueConnection *self;
    self = (TorqueConnection *) type->tp_alloc(type,0);
    if (self!=NULL)
    {
        self->server = PyString_FromString("");
        if (self->server == NULL) 
        {
            Py_DECREF(self);
            return NULL;
        }
        self->connection = 0;
    }
    return (PyObject *) self;
}

static int TorqueConnection_init(TorqueConnection *self, PyObject *args, PyObject *kwds)
{
    int con;
    char *err,*err_msg,*servername;
    static char *kwlist[] = {"server", NULL};
    servername = NULL;
    if (! PyArg_ParseTupleAndKeywords(args,kwds,"|s",kwlist, 
                &servername))
    {
        return -1;
    }

    if ((con = pbs_connect(servername))>=0)
    {
        self->connection = con;
        self->server = PyString_FromString(pbs_server);
        if ((self->server)==NULL) 
            return -1;
    }
    else
    {
        if ((err = pbs_geterrmsg(con))!=NULL)
        {
            self->connection = con;
            err_msg=malloc(sizeof(err)+24);
            sprintf(err_msg,"Torque Error Message: %s",err);
            PyErr_SetString(PyExc_RuntimeError,err_msg);
            free(err_msg);
            return -1;
        }
        else
        {
            self->connection = con;
            err_msg=malloc(sizeof(err)+24);
            sprintf(err_msg,"Torque Error Number: %i",con);
            PyErr_SetString(PyExc_RuntimeError,err_msg);
            free(err_msg);
            return -1;
        }
    }
    return 0;
}

static void
TorqueConnection_dealloc(TorqueConnection *self)
{
    Py_XDECREF(self->server);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject * TorqueConnection_inqueue(TorqueConnection *self, PyObject *args)
{
    struct batch_status *status,*current;
    struct attrl *attrib;
    PyObject *list,*name;
    struct attrl filter = {NULL,"Job_Name","",""};
    int cnt = 0;
    status = pbs_statjob(self->connection,"",&filter,"");
    current = status;
    while (current!=NULL)
    {
        cnt++;
        current = current->next;
    }
    if (!(list = PyList_New(cnt)))
        return NULL;
    current = status;
    int i =0;
    for (i=0; i<cnt; i++)
    {
        attrib = current->attribs;
        while (attrib!=NULL)
        {
            if (!(name=PyString_FromString(attrib->value)))
                return NULL;
            PyList_SET_ITEM(list,i,name);
            attrib = attrib->next;
        }
        current = current->next;
    }
    pbs_statfree(status);
    return list;
}

static PyObject * TorqueConnection_running(TorqueConnection *self, PyObject *args)
{
    struct batch_status *status,*current;
    struct attrl *attrib;
    PyObject *list,*name;
    struct attrl filter2 = {NULL,"Job_Name","",""};
    struct attrl filter1 = {&filter2,"job_state","",""};
    status = pbs_statjob(self->connection,"",&filter1,"");
    if ((list = PyList_New(0))==NULL)
    {
        PyErr_SetString(PyExc_RuntimeError,"Empyt list");
        return NULL;
    }
    current = status;
    while (current!=NULL)
    {
        attrib = current->attribs;
        while (attrib!=NULL)
        {
            if (strcmp(attrib->value,"R")==0)
            {
                attrib = attrib->next;
                if ((name=PyString_FromString(attrib->value))==NULL)
                {
                    PyErr_SetString(PyExc_RuntimeError,"String conversion error");
                    return NULL;
                }
                if (PyList_Append(list,name)==-1)
                    return NULL;
            }
            attrib=attrib->next;
        }
        current = current->next;
    }
    pbs_statfree(status);
    return list;
}

static PyObject * TorqueConnection_close(TorqueConnection * self, PyObject *args)
{
    pbs_disconnect(self->connection);
    self->connection = 0;
    Py_RETURN_NONE;
}

static PyMethodDef TorqueConnection_methods[] =
{
    {"inqueue", (PyCFunction)TorqueConnection_inqueue, METH_VARARGS, "Return a list of job names in queue."},
    {"running", (PyCFunction)TorqueConnection_running, METH_VARARGS, "Return a list of job names running now."},
    {"close", (PyCFunction)TorqueConnection_close, METH_VARARGS, "Close the connection to torque server."},
    {NULL,NULL,0,NULL}
};

static PyMemberDef TorqueConnection_members[] = 
{
    { "connection",  T_INT, offsetof(TorqueConnection, connection), 0,
        "Connection number." },
    { "server",  T_OBJECT, offsetof(TorqueConnection, server), 0,
        "Servername" },
    { NULL }
};


static PyTypeObject TorqueConnectionType =
    {
        PyObject_HEAD_INIT(NULL)
        0,                         /* ob_size */
        "TorqueConnection",               /* tp_name */
        sizeof(TorqueConnection),         /* tp_basicsize */
        0,                         /* tp_itemsize */
        (destructor)TorqueConnection_dealloc, /* tp_dealloc */
        0,                         /* tp_print */
        0,                         /* tp_getattr */
        0,                         /* tp_setattr */
        0,                         /* tp_compare */
        0,                         /* tp_repr */
        0,                         /* tp_as_number */
        0,                         /* tp_as_sequence */
        0,                         /* tp_as_mapping */
        0,                         /* tp_hash */
        0,                         /* tp_call */
        0,                         /* tp_str */
        0,                         /* tp_getattro */
        0,                         /* tp_setattro */
        0,                         /* tp_as_buffer */
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags*/
        "TorqueConnection object connects to a torque server.",        /* tp_doc */
        0,                         /* tp_traverse */
        0,                         /* tp_clear */
        0,                         /* tp_richcompare */
        0,                         /* tp_weaklistoffset */
        0,                         /* tp_iter */
        0,                         /* tp_iternext */
        TorqueConnection_methods,         /* tp_methods */
        TorqueConnection_members,         /* tp_members */
        0,                         /* tp_getset */
        0,                         /* tp_base */
        0,                         /* tp_dict */
        0,                         /* tp_descr_get */
        0,                         /* tp_descr_set */
        0,                         /* tp_dictoffset */
        (initproc)TorqueConnection_init,  /* tp_init */
        0,                         /* tp_alloc */
        TorqueConnection_new,      /* tp_new */
    };

static PyMethodDef torque_methods[] = 
{
    { NULL }
};

PyMODINIT_FUNC inittorque (void)
{
    PyObject * mod;
    mod =  Py_InitModule3("torque",torque_methods,"Juno's and Hermod's interface to TORQUE");

    if (mod==NULL) {
        return;

    }

    if (PyType_Ready(&TorqueConnectionType)<0) {
        return;
    }
    Py_INCREF(&TorqueConnectionType);
    PyModule_AddObject(mod,"TorqueConnection", (PyObject*) &TorqueConnectionType);
}


