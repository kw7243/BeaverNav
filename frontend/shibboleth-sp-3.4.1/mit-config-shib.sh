 #!/bin/sh

# Configure the Shibboleth SP for use with MIT Touchstone.

download_url="https://touchstone.mit.edu/config/shibboleth-sp-3/"
template_url="${download_url}shibboleth2.xml.in"
attrmap_url="${download_url}attribute-map.xml"

# MIT metadata signing cert location and fingerprints
md_cert_url="https://touchstone.mit.edu/certs/mit-md-cert.pem"
md_cert_fingerprint_sha1="1E:7E:47:64:EF:C9:42:94:7E:51:62:3E:51:EE:48:69:5E:97:CF:90"
md_cert_fingerprint_sha256="0B:65:DE:D2:38:47:48:08:D4:1D:19:EF:10:6E:DF:74:29:BD:D6:1C:DB:FA:65:34:70:A6:B5:A5:2A:74:74:8C"

support="touchstone-support@mit.edu"
files="shibboleth2.xml"

# Determine whether to use echo -n or \c to echo without a trailing newline.
case "`echo -n`" in
-n)
  n=''
  c='\c'
  ;;
*)
  n='-n'
  c=''
  ;;
esac

# Determine if the openssl command is in our PATH
if openssl version > /dev/null 2>&1 ; then
  have_openssl=true
else
  have_openssl=false
fi

echononewline()
{
  echo $n "$@$c"
}

canonicalize_hostname()
{
  case "$1" in
  *.*)
    name="$1"
    ;;    
  *)
    name="$1.mit.edu"
    ;;
  esac
  echo "$name" | tr '[:upper:]' '[:lower:]'
}

# Generate the self-signed certificate/key pair of files using the
# Shibboleth keygen script.  Any existing files are renamed.
generate_cert()
{
  prefix="$1"
  # Determine where the keygen script lives.  On Red Hat, it is in
  # the Shibboleth configuration directory (/etc/shibboleth).  On
  # Debian, it is in /usr/sbin/shib-keygen.
  if [ -x ./keygen.sh ]; then
    keygen="./keygen.sh"
  elif [ -x /usr/sbin/shib-keygen ]; then
    keygen="/usr/sbin/shib-keygen"
  else
    echo "Error: Shibboleth keygen script is not available." 1>&2
    echo "Please contact $support" 1>&2
    exit 1
  fi
  # Determine the user/group that should own the key files.
  # This will be "shibd" on RHEL, "_shibd" on Debian/Ubuntu.
  # This assumes the group name will be the same as the user.
  if id "shibd" >/dev/null 2>&1; then
    shibd_user="shibd"
  elif id "_shibd" >/dev/null 2>&1; then
    shibd_user="_shibd"
  else
    shibd_user="root"
  fi
  # Save any existing cert/key files, and regenerate.
  if [ -f "${prefix}-cert.pem" ]; then
    echo "Saving ${prefix}-cert.pem to ${prefix}-cert.pem.saved-by-mit-config-shib..." 1>&2
    mv "${prefix}-cert.pem" "${prefix}-cert.pem.saved-by-mit-config-shib"
  fi
  if [ -f "${prefix}-key.pem" ]; then
    echo "Saving ${prefix}-key.pem to ${prefix}-key.pem.saved-by-mit-config-shib..." 1>&2
    mv "${prefix}-key.pem" "${prefix}-key.pem.saved-by-mit-config-shib"
  fi
  echo "Generating ${prefix}-cert.pem and ${prefix}-key.pem..." 1>&2
  $keygen -b -h "$hostname" -n "$prefix" -u "$shibd_user" -g "$shibd_user" 1>&2 || exit 1
}

# Prompt for the path of an existing (certificate/key) file, and
# output it.
get_path()
{
  prompt="$1"
  default_path="$2"
  path=
  while [ -z "$path" ]; do
    echo "" 1>&2
    echononewline "Enter the path for the $prompt: " 1>&2
    if [ -f "$default_path" ]; then
      echononewline "[$default_path] " 1>&2
    fi
    read path
    case "$path" in
    "")
      if [ -f "$default_path" ]; then
        path="$default_path"
      else
        echo "Please enter a valid path." 1>&2
        path=
        continue
      fi
      ;;
    esac
    if [ ! -f "$path" ]; then
      echo "$path is not a valid file" 1>&2
      path=
    fi
  done
  echo "$path"
}

get_cert_path()
{
  prompt="$1"
  default_cert_prefix="$2"
  cert_path=
  while [ -z "$cert_path" ]; do
    cert_path=`get_path "$prompt" "${default_cert_prefix}-cert.pem"`
    if [ "$have_openssl" = true ]; then
      subject_hash=`openssl x509 -in "$cert_path" -noout -subject_hash 2>/dev/null`
      if [ $? -ne 0 ]; then
        echo "$cert_path does not appear to be a valid certificate." 1>&2
        cert_path=
        continue
      fi
      issuer_hash=`openssl x509 -in "$cert_path" -noout -issuer_hash 2>/dev/null`
      if [ "$issuer_hash" != "$subject_hash" ]; then
        echo "" 1>&2
        echo "Warning: Shibboleth should use a self-signed certificate." 1>&2
        cont=`get_yesno "Continue anyway" "Y"`
        if [ "$cont" = false ]; then
          cert_path=
          continue
        fi
      fi
      # Check that the certificate CN matches our host name.
      cn=`openssl x509 -in "$cert_path" -noout -subject -nameopt sep_multiline \
            | awk '/CN=/ { print substr($1,4); }'`
      case "$cn" in
      *$hostname*)
        ;;
      *)
        echo "The certificate's subject CN must match your web server host name." 1>&2
        echo "(The subject CN is $cn, given host name is $hostname)." 1>&2
        regen=`get_yesno "Generate a new (self-signed) certificate/key pair" "Y"`
        if [ "$regen" = false ]; then
          cont=`get_yesno "Continue anyway" "N"`
          if [ "$cont" = false ]; then
            echo "Please contact $support for further assistance." 1>&2
            exit 1
          fi
        else
          generate_cert "$default_cert_prefix"
          cert_path="${default_cert_prefix}-cert.pem"
        fi
        ;;
      esac
    fi
  done
  echo "$cert_path"
}

#    signing_key_path=`get_key_path "Shibboleth signing private key file" "$default_keypath" "$signing_cert_path"`
get_key_path()
{
  prompt="$1"
  default_key_path="$2"
  cert_path="$3"
  key_path=
  while [ -z "$key_path" ]; do
    key_path=`get_path "$prompt" "$default_key_path"`
    if [ "$have_openssl" = true ]; then
      # Check that it is a valid key file.
      if openssl rsa -noout -in "$key_path" > /dev/null 2>&1 ; then
        :
      else
        echo "$key_path does not appear to be a valid key file." 1>&2
        key_path=
        continue
      fi
      # Make sure the certificate and key files match.
      cert_mod=`openssl x509 -in "$cert_path" -noout -modulus | openssl md5`
      key_mod=`openssl rsa -in "$key_path" -noout -modulus | openssl md5`
      if [ "$cert_mod" != "$key_mod" ]; then
        echo "$cert_path and $key_path do not appear to be a matched pair." 1>&2
        key_path=
      fi
    fi
  done
  echo "$key_path"
}

# Ask a question with a yes/no answer, and output "true" or "false"
# accordingly.
get_yesno()
{
  prompt="$1"
  default_answer="$2"
  echo "" 1>&2
  echononewline "$prompt? [$default_answer] " 1>&2
  read answer
  if [ -z "$answer" ]; then
    answer="$default_answer"
  fi
  answer=`echo $answer | tr '[:upper:]' '[:lower:]'`
  case $answer in
  true|y|yes)
    answer=true
    ;;
  *)
    answer=false
    ;;
  esac
  echo "$answer"
}

default_hostname=`hostname`
default_hostname=`canonicalize_hostname "$default_hostname"`

# Make sure we are in the right place.
pkgsysconfdir=`pwd`
case "$pkgsysconfdir" in
/etc/shibboleth)
  prefix=/usr
  ;;
*/etc/shibboleth)
  prefix=`echo "$pkgsysconfdir" | sed -e 's:\(.*\)/etc/shibboleth$:\1:'`
  ;;
*)
  echo "Cannot determine Shibboleth install prefix." 1>&2
  echo "Please cd to the Shibboleth configuration directory to run this" 1>&2
  echo "(e.g. /etc/shibboleth or \$prefix/etc/shibboleth)." 1>&2
  exit 1
  ;;
esac

# Determine if wget or curl is available to download files.
if wget --version > /dev/null 2>&1 ; then
  download="wget -q -N"
elif curl --version > /dev/null 2>&1 ; then
  download="curl -s -O"
else
  download=
fi

# Download the template as needed or desired.
if [ -n "$download" ]; then
  if [ -e shibboleth2.xml.in ]; then
    get_template=`get_yesno "Download latest shibboleth2.xml.in" "Y"`
  else
    echo "Downloading $template_url..."
    get_template=true
  fi
  if [ "$get_template" = true ]; then
    $download "$template_url" || {
      echo "Error -- Failed to download $template_url" 1>&2
      echo "You must download this file in order to continue." 1>&2
      exit 1
    }
  fi
fi
if [ ! -e shibboleth2.xml.in ]; then
  echo "You must download $template_url in order to continue." 1>&2
  exit 1
fi

# Maybe download the latest attribute-map.xml.
got_attrmap=false
if [ -n "$download" ]; then
  get_attrmap=`get_yesno "Download latest attribute-map.xml" "Y"`
  if [ "$get_attrmap" = true ]; then
    echo "Saving previous version as attribute-map.xml.old" 1>&2
    cp -p attribute-map.xml attribute-map.xml.old
    $download "$attrmap_url"
    if [ $? -ne 0 ]; then
      echo "Warning -- Failed to download $attrmap_url" 1>&2
    else
      got_attrmap=true
    fi
  fi
fi
if [ "$got_attrmap" = false ]; then
  echo "Please make sure you have a current version of attribute-map.xml" 1>&2
  echo "You can download it from $attrmap_url" 1>&2
fi

while [ -z "$hostname" ]; do
  echo ""
  echononewline "Enter the web server host name: [$default_hostname] "
  read hostname
  if [ -z "$hostname" ]; then
    hostname="$default_hostname"
  fi
  hostname=`canonicalize_hostname "$hostname"`
done

case `uname` in
SunOS)
  files="$files shibd shibd-wrapper"
  if [ -d "/usr/athena/lib" ]; then
    default_ssldir=/usr/athena/lib
  elif [ -d "/usr/local/ssl/lib" ]; then
    default_ssldir=/usr/local/ssl/lib
  fi
  while [ -z "$ssldir" ]; do
    echo ""
    echononewline "Enter the OpenSSL library directory: [$default_ssldir] "
    read ssldir
    if [ -z "$ssldir" ]; then
      ssldir="$default_ssldir"
    fi
    if [ ! -d "$ssldir" ]; then
      echo "$ssldir is not a valid directory" 1>&2
      ssldir=
    fi
  done
  ;;
Linux)
  if [ -d "/usr/athena/lib" ]; then
    ssldir=/usr/athena/lib
  else
    ssldir=/lib
  fi
  ;;
esac

# Prompt for the certificate and key files.  We prefer to use the
# self-signed pairs usually generated at install time.

# for signing...
if [ ! -f sp-signing-cert.pem ]; then
  gen_cert=`get_yesno "Generate signing certificate/key pair" "Y"`
  if [ "$gen_cert" = true ]; then
    generate_cert "sp-signing"
  fi
fi

# for encryption...
if [ ! -f sp-encrypt-cert.pem ]; then
  gen_cert=`get_yesno "Generate encryption certificate/key pair" "Y"`
  if [ "$gen_cert" = true ]; then
    generate_cert "sp-encrypt"
  fi
fi

signing_cert_path=
while [ -z "$signing_cert_path" ]; do
  signing_key_path=
  #signing_cert_path=`get_path "Shibboleth signing certificate file" "sp-signing-cert.pem"`
  signing_cert_path=`get_cert_path "Shibboleth signing certificate file" "sp-signing"`

  echo "Please include the contents of $signing_cert_path when you register the server."

  # Get the key file.
  if [ "$signing_cert_path" = "sp-signing-cert.pem" ]; then
    default_key_path="sp-signing-key.pem"
  else
    default_key_path=""
  fi

  signing_key_path=`get_key_path "Shibboleth signing private key file" "$default_key_path" "$signing_cert_path"`
  if [ -z "$signing_key_path" ]; then
    # Here when the key and cert files do not match; start over.
    signing_cert_path=
    continue
  fi
done

encrypt_cert_path=
while [ -z "$encrypt_cert_path" ]; do
  encrypt_key_path=
  encrypt_cert_path=`get_cert_path "Shibboleth encryption certificate file" "sp-encrypt"`

  echo "Please include the contents of $encrypt_cert_path when you register the server."

  # Get the key file.
  if [ "$encrypt_cert_path" = "sp-encrypt-cert.pem" ]; then
    default_key_path="sp-encrypt-key.pem"
  else
    default_key_path=""
  fi

  encrypt_key_path=`get_key_path "Shibboleth encryption private key file" "$default_key_path" "$encrypt_cert_path"`
  if [ -z "$encrypt_key_path" ]; then
    # Here when the key and cert files do not match; start over.
    encrypt_cert_path=
    continue
  fi
done

handlerSSL=`get_yesno "Always use SSL for Shibboleth handler" "Y"`

cookie_props="http"
if [ "$handlerSSL" = true ]; then
  secure=`get_yesno "Set cookies secure (requires SSL for all protected content)" "Y"`
  if [ "$secure" = true ]; then
    cookie_props="https"
    echo ""
    echo "To avoid loops, be sure to redirect any non-https requests to SSL."
    echononewline "Enter <return> to continue: "
    read junk
  fi
fi

# Get the contact email address.
case "$hostname" in
*.*.*)
  default_contact=`echo "$hostname" | sed -e 's/\./-help@/'`
  ;;
*.*)
  default_contact="help@$hostname"
  ;;
*)
  default_contact="$hostname-help@mit.edu"
  ;;
esac
echo ""
echononewline "Support contact email address? [$default_contact] "
read contact
if [ -z "$contact" ]; then
  contact="$default_contact"
fi

if [ -n "$download" ]; then
  need_md_cert=true
  if [ -f mit-md-cert.pem ]; then
    if [ "$have_openssl" = true ]; then
      fingerprint=`openssl x509 -noout -fingerprint -sha256 -in mit-md-cert.pem 2>/dev/null | sed -e 's/^[^=]*=//'`
    fi
    if [ "$fingerprint" = "$md_cert_fingerprint_sha256" ]; then
      need_md_cert=false
    else
      cp -p mit-md-cert.pem mit-md-cert.pem.old
    fi
  fi
  if [ "$need_md_cert" = true ]; then
    echo "Downloading the MIT metadata signing certificate..."
    $download "$md_cert_url" || {
      echo "Warning -- Failed to download $md_cert_url" 1>&2
      echo "You must download this certificate in order to validate" 1>&2
      echo "the MIT metadata." 1>&2
    }
    if [ "$have_openssl" = true ]; then
      fingerprint=`openssl x509 -noout -fingerprint -sha256 -in mit-md-cert.pem | sed -e 's/^[^=]*=//'`
      if [ "$fingerprint" != "$md_cert_fingerprint_sha256" ]; then
        echo "Warning -- fingerprint mismatch on downloaded MIT signing certificate." 1>&2
        echo "Please contact $support for assistance." 1>&2
        exit 1
      fi
    fi
  fi
else
  echo "You must download the MIT metadata signing certificate" 1>&2
  echo "from $md_cert_url" 1>&2
  echo "in order to validate the MIT metadata." 1>&2
fi
echo ""

incommon=`get_yesno "Will this server be joining the InCommon Federation" "N"`
if [ "$incommon" = true ]; then
  begin_incommon='<!-- Begin InCommon addition -->'
  end_incommon='<!-- End InCommon addition -->'
  if [ ! -e inc-md-cert-mdq.pem ]; then
    url="http://md.incommon.org/certs/inc-md-cert-mdq.pem"
    if [ -n "$download" ]; then
      echo "Downloading InCommon metadata signing certificate..."
      $download "$url" || {
        echo "Warning -- Failed to download $url" 1>&2
        echo "You must download this certificate in order to validate" 1>&2
        echo "the published InCommon metadata." 1>&2
      }
      if [ "$have_openssl" = true ]; then
        fingerprint=`openssl x509 -noout -fingerprint -sha1 -in inc-md-cert-mdq.pem | sed -e 's/^[^=]*=//'`
        if [ "$fingerprint" != "F8:4E:F8:47:EF:BB:EE:47:86:32:DB:94:17:8A:31:A6:94:73:19:36" ]; then
          echo "Warning -- fingerprint mismatch on downloaded InCommon signing certificate." 1>&2
          echo "Please contact $support for assistance." 1>&2
          exit 1
        fi
      fi
    else
      echo "You must download the InCommon metadata signing certificate" 1>&2
      echo "from $url" 1>&2
      echo "in order to validate the published InCommon metadata." 1>&2
    fi
    echo ""
  fi
else
  begin_incommon='<!--'
  end_incommon='-->'
fi

echo "Using prefix $prefix..."
pkgxmldir=$prefix/share/xml/shibboleth
libexecdir=$prefix/libexec
# XXX
varrundir=/var/run

for file in $files ; do
  tmpfile=$file.$$
  sed -e "s:%%HOSTNAME%%:$hostname:" \
      -e "s:%%SSLDIR%%:$ssldir:" \
      -e "s:%%SIGNINGKEYPATH%%:$signing_key_path:" \
      -e "s:%%SIGNINGCERTPATH%%:$signing_cert_path:" \
      -e "s:%%ENCRYPTKEYPATH%%:$encrypt_key_path:" \
      -e "s:%%ENCRYPTCERTPATH%%:$encrypt_cert_path:" \
      -e "s:%%HANDLERSSL%%:$handlerSSL:" \
      -e "s:%%COOKIEPROPS%%:$cookie_props:" \
      -e "s:%%CONTACT_EMAIL%%:$contact:" \
      -e "s:%%BEGIN_INCOMMON%%:$begin_incommon:" \
      -e "s:%%END_INCOMMON%%:$end_incommon:" \
      -e "s:@-PKGXMLDIR-@:$pkgxmldir:" \
      -e "s:@-PKGSYSCONFDIR-@:$pkgsysconfdir:" \
      -e "s:@-LIBEXECDIR-@:$libexecdir:" \
      -e "s:@-VARRUNDIR-@:$varrundir:" \
      -e "s:@-PREFIX-@:$prefix:" \
    < $file.in > $tmpfile || exit 1
  if [ -f "$file" ]; then
    echo "$file already exists, saving previous version as $file.old" 1>&2
    mv $file $file.old
  fi
  case $file in
  shibd-wrapper)
    mv $tmpfile $prefix/sbin/$file
    chmod 755 $prefix/sbin/$file
    ;;
  *)
    mv $tmpfile $file
    chmod 644 $file
    ;;
  esac
done
