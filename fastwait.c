#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *
method_fastwait(PyObject *self, PyObject *args)
{
  static double recv_byte = 0;
  
  double* buff;
  if (!PyArg_ParseTuple(args, "p", &buff))
        return NULL;

  while(buff[0] != recv_byte){}
  recv_byte += 1;
  recv_byte = (double)((int)recv_byte % 2);
    
   

	      
  return args;
}


static PyMethodDef FastWaitMethods[] = {
    {"fastwait", method_fastwait, METH_VARARGS, "Python interface to wait on a file"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef fastwaitmodule = {
    PyModuleDef_HEAD_INIT,
    "fast wait",
    "Python interface to wait on a mmaped file in a busy loop",
    -1,
    FastWaitMethods
};


PyMODINIT_FUNC PyInit_fastwait(void) {
    return PyModule_Create(&fastwaitmodule);
}
