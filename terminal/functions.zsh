function whohasport(){
  lsof -i tcp:$1
}