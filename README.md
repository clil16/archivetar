# Archive Tar -- A Tar for use with HSM Systems

Archive tar, is a wrapper around GNU Tar and a few other tools.  It was mostly made to use with [Data Den](https://arc-ts.umich.edu/data-den/) but can be used by any system that expects large files but not to large.


# TODO

- Add check for GNU Tar
- Add split support
  - Adjust split size from variable
- Generate an index
- Check if output file already exists and bail
- Add option to sum data and prompt to continue
