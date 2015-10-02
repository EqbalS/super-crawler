# super-crawler
This is a web crawler that uses a YAML config file to do some action on some selected elements of a web page.

## Example
This is the sample config file in `test-conf.yml`.
```
deviantart:
    address: http://www.deviantart.com/tag/batman
    item:
        css-selector: span.shadow > a.thumb
        attribute: href
    name: deviantart
    follow:
        item:
            css-selector: div.dev-page-view > div.dev-view-main-content > div.dev-view-deviation img.dev-content-full
            attribute: src
        download: true
```
You have to run:
```
super-crawler test-conf.yml
```
Then it will get the `http://www.deviantart.com/tag/batman` page and follow the picture links and the in each picture page download the image.
