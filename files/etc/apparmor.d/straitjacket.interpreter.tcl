#include <tunables/global>

#/usr/bin/tclsh8.5 flags=(complain) {
profile straitjacket/interpreter/tcl {
  #include <abstractions/base>
  #include <abstractions/straitjacket-base>

  # I'm not sure why this is required. Without this tclsh
  # complains about 'Tcl_InitNotifier: unable to start notifier thread'
  # Since I'm not a tcl developer I don't know its execution model
  # and therefore found this value via trial and error to work
  set rlimit nproc <= 10,

  /usr/lib/libtcl* mr,
  /lib/x*-linux-gnu/lib* mr,
  /usr/bin/tclsh8.5 mrix,
  /var/local/straitjacket/tmp/source/?*/?* r,
  /usr/shared/tcltk/tcl8.5/* r,
}
