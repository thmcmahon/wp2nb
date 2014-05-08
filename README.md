wp2nb - Convert wordpress blog to nationbuilder
================================================

Converts wordpress xml to nationbuilder JSON then uploads to nationbuilder.

This script will upload any images hosted on wordpress to the relevant post and show them at the top of the post.

The script will also extract any youtube URLs and append them to the end of a post.

This script depends on python. You will need pip installed to install the dependencies.

Usage
=====

1. Clone the repository and enter it

```bash
git clone https://github.com/thmcmahon/wp2nb.git
cd wp2nb
````

2. Set environment variables for your nationbuilder token and your site's slug. You can grab a token from your site's nationbuilder admin page. This will work on a mac or linux, the windows command will be different.

```bash
export NB_TOKEN=yourtokengoeshere
export SITE_SLUG=yoursitesluggoeshere
```

3. Install any python dependencies that you are missing

```bash
pip install -r requirements.txt
```

4. Check that your wordpress xml is valid with xmllint, if not fix any errors before proceeding to upload. It should print the file in full to stdout if there are no errors.

```bash
xmllint input_file.xml
```

5. Run the script. It will output the response codes for each upload, so hopefully you will see a series of '200's in your terminal to indicate that it is working. This script will take a while to run.

```bash
python wp2nb.py input_file.xml
```

6. Update your nationbuilder theme to include the attached images in your blog posts. You'll need a small snippet of liquid template code in your blog post's template. See: http://nationbuilder.com/liquid_template_examples.

```html
{% for attachment in page.attachments limit:10  %}
<img src="{{ attachment.url }}" />
{% endfor %}
```