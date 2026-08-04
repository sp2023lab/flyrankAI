# DNS Walkthrough for My Future FlyRank Subdomain

## What DNS does

DNS connects a human-readable name to the online service that should answer for it. Instead of a visitor needing to know a server address, they can type a name such as `shyam.flyrank.ai`. DNS tells their device where that name ultimately points.

## Resolver and nameserver

When someone enters the address, the browser asks a DNS resolver for help. The resolver may already have the answer cached. If it does not, it follows the DNS hierarchy until it reaches the authoritative nameserver for `flyrank.ai`. That nameserver stores the official DNS records created by FlyRank Ops.

## The CNAME record

A CNAME record makes one hostname an alias of another hostname. It does not move, copy or rebuild the website. It tells DNS that one name should follow another name.

My planned record would be:

```text
Record type: CNAME
Host/name: shyam
Target/value: sp2023lab.netlify.app
```

This would make `shyam.flyrank.ai` point to the Netlify hostname already serving my portfolio.

## What happens when someone visits

1. The visitor types `shyam.flyrank.ai`.
2. Their browser asks a DNS resolver where that hostname points.
3. The resolver checks the authoritative nameserver for `flyrank.ai`.
4. The nameserver returns the CNAME record for `shyam`.
5. The resolver follows the record to `sp2023lab.netlify.app`.
6. Netlify identifies the site connected to the custom domain.
7. Netlify sends the website files to the visitor's browser.
8. The browser displays the portfolio.

## HTTPS

After the custom domain is added in Netlify, Netlify verifies that the DNS record points to the correct site. It then provisions an SSL/TLS certificate for the custom hostname. Once the certificate is active, the portfolio loads through HTTPS and the browser displays the padlock. The site does not need to be rebuilt because the custom domain is a pointer to the same deployed files.
