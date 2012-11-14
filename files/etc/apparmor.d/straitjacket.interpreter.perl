#include <tunables/global>

profile straitjacket/interpreter/perl {
  #include <abstractions/base>
  #include <abstractions/straitjacket-base>

  /var/local/straitjacket/tmp/source/?*/?* r,
  /usr/share/perl/** r,
  /usr/share/perl5/** r,
  /usr/lib/perl/** rix,
  /usr/lib/perl5/** rix,
}
