# Two of Three File Recovery Tool (Python 3)

**Recover an original file from 3 different corrupted copies (2-of-3 Recovery)**

Main function iterates through 3 corrupted copies and simply compares them byte-by-byte.
If at least 2 corrupted versions have the equal value for the same byte location,
then we keep the value for reconsturcting the original file as 
we can have high level of confidence that it is same value as in the original file.

In case the byte value is corrupted at the same location in 2 seperate copies, 
we get 3 different values for the same byte and we can no longer determine
which one we should keep. Therefore we create 3 different new branches 
for the recovered bytes and temporarily keep all of the 3 values in these new branches.

At the end of bytes reconstruction phase we may end up with many versions based on branches.

And finally we look at the checksums of these temporary recovery branches 
and look for a match with the original file hash to verify that we have 
a recovery branch 100% same as the original file.


## Notes:

Branching level increases resource intensity exponentially


Cannot recover files under these conditions:	

* Bit-level corruption happened simultaneosly in 2 seperate copies, which is extremely unlikely.

* If corrupted file lengths are different then the current byte comparison algorithm won't work properly.