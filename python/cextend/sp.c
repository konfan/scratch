#include <Python.h>


static PyObject *
sp_test(PyObject *self, PyObject * args) {
    const char * command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command))
        return NULL;
    sts = system(command);
    return Py_BuildValue("i", sts);
}


static PyMethodDef SPMethods[] = {
    {
        "test", sp_test, METH_VARARGS,
        "None"},
    {0,0,0,0}
};

PyMODINIT_FUNC
initsp(void) {
    (void) Py_InitModule("sp", SPMethods);
}

int 
main(int argc, char * argv[]) {
    Py_SetProgramName(argv[0]);
    Py_Initialize();
    initsp();
    return 0;
}
