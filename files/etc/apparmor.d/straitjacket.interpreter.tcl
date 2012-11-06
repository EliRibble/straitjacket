#include <tunables/global>

#/usr/bin/tclsh8.5 flags=(complain) {
profile straitjacket/interpreter/tcl {
  #include <abstractions/base>
  #include <abstractions/straitjacket-base>

  set rlimit nproc <= 11,

  /usr/lib/libtcl* mr,
  /lib/x*-linux-gnu/lib* mr,
  /usr/bin/tclsh8.5 mrix,
  /var/local/straitjacket/tmp/source/?*/?* r,
  /usr/shared/tcltk/tcl8.5/* r,

  #/etc/nsswitch.conf
  #/etc/passwd
  /usr/share/tcltk/tcl8.5/init.tcl r,
}
