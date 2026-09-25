

patch -p1 < patches/overridden.patch
# A wheels repo gyökerében
echo "A wheels-repo gyökerében kell!"
patch -p1 < arm32-sigbus-fix.patch
