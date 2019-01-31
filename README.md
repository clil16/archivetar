# Archive Tar -- A Tar for use with HSM Systems

Archive tar, is a wrapper around GNU Tar and a few other tools.  It was mostly made to use with [Data Den](https://arc-ts.umich.edu/data-den/) but can be used by any system that expects large files but not to large.

# Dry-Run

Because Archive Tar is to work with massive datasets, the `-d` dry run / debug option should be used to evaulate the commands that will be run without actually running them.

# Backups

Archive tar uses GNU Tar [Incremental Dumps](http://www.gnu.org/software/tar/manual/html_node/Incremental-Dumps.html) if backups are enabled.  You must add `-b <pathto.snar>`  and the same snar must be given each run, whiel the tar filename must be updated to not overwrite the old one.

The snar file tracks the changes made *including deletions* but is not required to extract.

```
# Initial copy of data (outdata.snar doesn't exist)
archivetar -v -f outdata.0.tar -b outdata.snar  -s vis-human/
```

# split

Many HSM / Tape or cloud object systems have a maximum filesize. Or uploads can be unreliable.  If given the `-s` option archivetar will split the tar archive into 200GB chunks.  Note if any one of these is lost or corrupted it is unlikely you can recover any of your data.

If using compression it is applied before the split currently.  Making data recovery if one entry is lose that much less likely.

To extract use cat:

```
cat outdata.tar-part-* | tar -xvf -  

# extract compressed archive with parallel decompressor
cat outdata.tar.bz2-part-* | tar -xvf - --use-compress-program=lbzip2
```

# TODO

- Add check for GNU Tar
- Generate an index
- Check if output file already exists and bail
- Add option to sum data and prompt to continue
