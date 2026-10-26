"""Isolated Hugo rendering and dependency-free DOM behavior tests.
Run: HUGO_BIN=/tmp/hugo-performance/hugo python3 -m unittest discover -s tests -p test_deferred_embeds.py -v
"""
import html.parser
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = 'https://www.komoot.com/de-de/tour/123/embed?share_token=secret&profile=1'


class Tags(html.parser.HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        for folder in ('layouts/_shortcodes', 'layouts/_partials', 'assets'):
            shutil.copytree(ROOT / folder, cls.root / folder)
        (cls.root / 'hugo.toml').write_text('baseURL="https://example.org/"\ndefaultContentLanguage="de"\n[languages.de]\nweight=1\n[languages.en]\nweight=2\n')
        (cls.root / 'layouts/_default').mkdir()
        (cls.root / 'layouts/_default/single.html').write_text('{{ .Content }}{{ if .Params.comments }}{{ partial "comments.html" . }}{{ end }}')
        (cls.root / 'content').mkdir()
        for lang in ('de', 'en'):
            (cls.root / f'content/embed.{lang}.md').write_text('+++\ntitle="Embed"\ncomments=true\n+++\n' + '{{< komoot src="' + SRC + '" height="480" >}}\n' + '{{< komoot src="' + SRC + '" >}}\n')
        (cls.root / 'content/plain.de.md').write_text('+++\ntitle="Plain"\n+++\nPlain')
        (cls.root / 'content/unsafe.de.md').write_text('+++\ntitle="Unsafe"\n+++\n{{< komoot src="https://www.komoot.com.evil.test/tour/123/embed" height="bad" >}}\n{{< komoot src="javascript:alert(1)" >}}')
        result = subprocess.run([os.environ.get('HUGO_BIN', '/tmp/hugo-performance/hugo'), '--source', str(cls.root), '--quiet'], text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(result.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def page(self, path):
        return (self.root / 'public' / path / 'index.html').read_text()

    def test_komoot_has_no_eager_frame_and_preserves_url_dimensions(self):
        text = self.page('embed')
        tags = Tags(text).tags
        self.assertFalse(any(tag == 'iframe' for tag, _ in tags))
        boxes = [a for _, a in tags if a.get('data-deferred-embed') == 'komoot']
        self.assertEqual(len(boxes), 2)
        self.assertEqual(boxes[0]['data-src'], SRC)
        self.assertEqual(boxes[0]['data-height'], '480')
        self.assertIn('480px', boxes[0]['style'])
        self.assertEqual(boxes[1]['data-height'], '700')
        self.assertTrue(any(t == 'a' and a.get('href') == SRC for t, a in tags))
        self.assertIn('Karte laden', text)
        self.assertIn('Load map', self.page('en/embed'))

    def test_giscus_settings_and_no_remote_script(self):
        tags = Tags(self.page('embed')).tags
        self.assertFalse(any(t == 'script' and 'giscus.app' in a.get('src', '') for t, a in tags))
        comments = next(a for _, a in tags if a.get('data-deferred-embed') == 'giscus')
        for key, value in {'repo': 'matsch1/web', 'repo-id': 'R_kgDOOj9vMw', 'category': 'Announcements', 'category-id': 'DIC_kwDOOj9vM84CzTmb', 'mapping': 'pathname', 'strict': '0', 'reactions-enabled': '1', 'emit-metadata': '0', 'input-position': 'top', 'theme': 'dark_protanopia', 'lang': 'de'}.items():
            self.assertEqual(comments['data-' + key], value)
        self.assertIn('https://github.com/matsch1/web/discussions', self.page('embed'))
        en = next(a for _, a in Tags(self.page('en/embed')).tags if a.get('data-deferred-embed') == 'giscus')
        self.assertEqual(en['data-lang'], 'en')

    def test_script_fingerprinted_deduplicated_and_only_when_needed(self):
        scripts = [a for t, a in Tags(self.page('embed')).tags if t == 'script']
        self.assertEqual(len(scripts), 1)
        self.assertRegex(scripts[0]['src'], r'deferred-embeds(?:\.min)?\.[a-f0-9]+\.js$')
        self.assertIn('integrity', scripts[0])
        self.assertNotIn('<script', self.page('plain'))

    def test_untrusted_urls_are_not_rendered(self):
        text = self.page('unsafe')
        self.assertNotIn('<iframe', text)
        self.assertNotIn('data-src=', text)
        self.assertNotIn('href=', text)
        self.assertNotIn('javascript:', text)


class BehaviorTests(unittest.TestCase):
    def test_activation_observation_retry_and_url_validation(self):
        script = ROOT / 'assets/js/deferred-embeds.js'
        self.assertTrue(script.exists(), 'deferred embed controller missing')
        result = subprocess.run(['node', '-e', NODE_TEST, str(script)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


NODE_TEST = r'''
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
class Element {
  constructor(tag='div', dataset={}) { this.tagName=tag; this.dataset=dataset; this.children=[]; this.listeners={}; this.attrs={}; this.hidden=false; this.disabled=false; this.textContent='Load'; }
  setAttribute(k,v) { this.attrs[k]=String(v); }
  getAttribute(k) { return this.attrs[k]; }
  addEventListener(k,fn) { this.listeners[k]=fn; }
  appendChild(el) { this.children.push(el); return el; }
  remove() { this.removed=true; }
  querySelector(s) { if(s==='[data-embed-load]') return this.button; if(s==='[data-embed-status]') return this.status; if(s==='[data-embed-target]') return this.target; return null; }
  click() { if(!this.disabled) this.listeners.click?.(); }
}
function box(type, extra={}) { const el=new Element('section',{deferredEmbed:type,src:'https://www.komoot.com/tour/123/embed?share_token=x&profile=1',height:'480',title:'Map',loading:'Loading',error:'Failed',retry:'Retry',...extra}); el.button=new Element('button'); el.status=new Element(); el.target=new Element(); return el; }
function run(observer=true) {
 const map=box('komoot'), comments=box('giscus',{repo:'matsch1/web',lang:'de'}), bad=box('komoot',{src:'https://www.komoot.com.evil.test/tour/123/embed'});
 const observers=[];
 const document={readyState:'complete',querySelectorAll:()=>[map,comments,bad],createElement:t=>new Element(t)};
 const context={document, URL, setTimeout:()=>1,clearTimeout:()=>{},window:{}};
 if(observer) context.IntersectionObserver=class { constructor(cb,options){ this.cb=cb; this.options=options; observers.push(this); } observe(el){this.el=el;} unobserve(el){this.unobserved=el;} };
 vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),context);
 return {map,comments,bad,observers};
}
let {map,comments,bad,observers}=run();
assert.equal(map.target.children.length,0); assert.equal(comments.target.children.length,0);
assert.equal(observers.length,1); assert.equal(observers[0].el,comments);
map.button.click(); map.button.click();
assert.equal(map.target.children.length,1);
assert.equal(map.target.children[0].src,map.dataset.src);
assert.equal(map.target.children[0].height,'480');
bad.button.click(); assert.equal(bad.target.children.length,0);
observers[0].cb([{isIntersecting:false,target:comments}]); assert.equal(comments.target.children.length,0);
observers[0].cb([{isIntersecting:true,target:comments}]);
assert.equal(comments.target.children.length,1);
let script=comments.target.children[0]; assert.equal(script.src,'https://giscus.app/client.js');
assert.equal(script.attrs['data-repo'],'matsch1/web'); assert.equal(script.attrs['data-lang'],'de');
comments.button.click(); assert.equal(comments.target.children.length,1);
script.onerror(); assert.equal(comments.button.disabled,false); assert.equal(comments.button.hidden,false); assert.equal(comments.status.textContent,'Failed');
comments.button.click(); assert.equal(comments.target.children.length,2); assert.equal(script.removed,true);
comments.target.children[1].onload(); assert.equal(comments.button.hidden,true);
let fallback=run(false); assert.equal(fallback.comments.target.children.length,0); fallback.comments.button.click(); assert.equal(fallback.comments.target.children.length,1);
console.log('Deferred embed behavior OK');
'''
