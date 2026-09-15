<?php
/** Local/staging protections: captured forms must never submit to production. */
add_filter('pre_wp_mail', '__return_false');
add_filter('pre_option_blog_public', function () { return '0'; });
add_action('send_headers', function () { header('X-Robots-Tag: noindex, nofollow'); });
add_action('wp_footer', function () { ?>
<script>document.addEventListener('submit',function(e){e.preventDefault();alert('Migration preview: this form is not connected.');},true);</script>
<?php });
