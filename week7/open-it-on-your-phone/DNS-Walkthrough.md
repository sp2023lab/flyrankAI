# DNS Walkthrough for My Future FlyRank Subdomain

DNS connects a human-readable name to the online service that should answer for it. When someone enters `shyam.flyrank.ai`, their browser asks a DNS resolver where that hostname points. The resolver may use a cached answer; otherwise it follows the DNS hierarchy until it reaches the authoritative nameserver for `flyrank.ai`, which stores the official records created by FlyRank Ops.

A CNAME record makes one hostname an alias of another. It does not move or rebuild the website. My planned record would be:

```text
Record type: CNAME
Host/name: shyam
Target/value: sp2023lab.netlify.app
```

The resolver receives that record, follows it to Netlify, and Netlify serves the files belonging to my portfolio project. After I add the custom domain in Netlify, Netlify verifies the DNS record and provisions an SSL/TLS certificate. The same deployed site then loads through HTTPS at the FlyRank subdomain without a migration or rebuild.
