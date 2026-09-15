<?php
/** Test-environment email and indexing controls. CiviCRM mail needs its own setting. */
if (in_array(wp_get_environment_type(), ['local', 'development', 'staging'], true)) {
    add_filter('pre_wp_mail', '__return_false');
    add_filter('pre_option_blog_public', function () { return '0'; });
    add_action('send_headers', function () { header('X-Robots-Tag: noindex, nofollow'); });
}
// Archived forms are inert. New native WordPress/CiviCRM pages may submit normally.
add_action('wp_footer', function () {
    if (!is_singular() || !get_post_meta(get_queried_object_id(), '_labg_source_url', true)) { return; }
    ?>
<script>document.addEventListener('submit',function(e){e.preventDefault();alert('Migration preview: this archived form is not connected.');},true);</script>
<?php });
