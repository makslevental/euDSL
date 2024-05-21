set(LLVM_LINK_COMPONENTS Core Support TargetParser)

add_executable(foo main.cpp)

target_link_libraries(
  foo PRIVATE clangAST clangBasic clangCodeGen
  clangFrontend clangLex clangParse clangSerialization)
