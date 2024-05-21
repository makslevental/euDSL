# euDSL
A good DSL

```
-DLLVM_ENABLE_LTO=ON
-DCMAKE_C_FLAGS=-save-temps=obj
-DCMAKE_CXX_FLAGS=-save-temps=obj
```

or 

```
CC=$(which wllvm)
CXX=$(which wllvm++)
LLVM_COMPILER=clang
cmake ..
# gotta be make...
make
extract-bc -b src/LinearMath/libLinearMath.a
```

Note you might have to `export WLLVM_CONFIGURE_ONLY=1` first in order to run tblgen successfully.