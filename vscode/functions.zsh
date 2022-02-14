if test "$(expr substr $(uname -s) 1 5)" = "Linux"
then
    function code() { (flatpak run com.visualstudio.code $*) }
fi