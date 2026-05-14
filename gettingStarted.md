# Executing a run



To execute a run, enter

```

C:\HTAP\recover> ruby C:/HTAP/htap-prm.rb -r test.run -c -k -t 7  

```

## Notes

- This is run from the directory the project is saved at ("recover" in this case)

- the path for htap-prm.rb musty be specified if not running from the directory it's in ("C:/HTAP" in this caase)

- "-k" keeps the files from the run

- "-t" specifies the number of threads used (7 in this example)

