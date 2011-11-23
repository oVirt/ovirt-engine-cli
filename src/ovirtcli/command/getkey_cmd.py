# Extract a private key from a Java key store. The standard program
# "keytool" that is part of the JRE unfortunately doesn't have this
# functionality (presumably because of 'security' reasons).
#
# The simplest way to do this, would be to convert the key store to PKCS12
# format, and then use openssl to extract the private key (OpenSSL does have
# this functionality). However for some reason, the required command
# "keytool -importkeystore -deststoretype PKCS12" often hangs for me. I was
# not able to determine the cause of this behavior.
#
# So the option taken here is to use a small Java program that uses the Java
# API to extract the private key. This means that we're adding a dependency on
# the JDK.
#
# Why this "Java in shell" hack instead of a proper Java program? Because I
# know that the system from which i created this script has the JDK installed,
# and it saves me from having to distribute compiled versions.
#
# I took inspiration for the Java program from:
# http://mark.foster.cc/pub/java/ExportPriv.java
#
# This file is licensed under the MIT license, see
# http://www.opensource.org/licenses/mit-license.php

dumpkey_function = """
function dumpkey()
{
    if [ "$#" -ne "3" ]; then
        echo "usage: $0 <keystore> <alias> <password>"
        exit 1
    fi

    tmpdir="`mktemp -d`"
    cat <<EOM > "$tmpdir/extractkey.java"
import java.security.Key;
import java.security.KeyStore;
import java.io.FileDescriptor;
import java.io.FileInputStream;
import java.io.FileOutputStream;

class extractkey
{
    static public void main(String[] args) throws Exception
    {
        String fname = "$1";
        String alias = "$2";
        char[] password = new String("$3").toCharArray();

        KeyStore store = KeyStore.getInstance("JKS");
        FileInputStream fin = new FileInputStream(fname);
        store.load(fin, password);
        Key key = store.getKey(alias, password);
        FileOutputStream fout = new FileOutputStream(FileDescriptor.out);
        fout.write(key.getEncoded());
    }
}
EOM
    javac "$tmpdir/extractkey.java"

    echo "-----BEGIN PRIVATE KEY-----"
    java -cp "$tmpdir" extractkey | base64
    echo "-----END PRIVATE KEY-----"

    rm -rf -- "$tmpdir"
}
"""
