#include <tunables/global>

profile straitjacket/compiler/scala {
  #include <abstractions/base>
  #include <abstractions/straitjacket-base>
  #include <abstractions/straitjacket-jvm>

  /bin/uname rix,
  /usr/bin/scalac rix,
  /usr/lib/jvm/*/bin/java rix,
  /var/local/straitjacket/tmp/source/?*/?* rw,

}
