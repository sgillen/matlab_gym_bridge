#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

static PyObject *
method_fastwait(PyObject *self, PyObject *args)
{
  static double recv_byte = 1;
  double* buff;

  printf("hello\n");
  if (!PyArg_ParseTuple(args, "k", &buff))
        return NULL;

  printf("buff: %p \n", buff);
  printf("hello2\n");
  while(buff[0] != recv_byte){}
  printf("hello3\n");
  recv_byte += 1;
  printf("hello4\n");
  recv_byte = (double)((int)recv_byte % 2);
  printf("hello5\n");
   
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
