<?php
// Captured markup is an interim visual reference; native content remains editable.
$head = get_post_meta(get_queried_object_id(), '_labg_head', true);
$body = get_post_meta(get_queried_object_id(), '_labg_body_attributes', true);
$html = get_post_meta(get_queried_object_id(), '_labg_html_attributes', true);
?><!doctype html>
<html <?php echo $html ?: 'lang="en-US"'; ?>>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<?php echo $head; wp_head(); ?></head>
<body <?php echo $body; ?>><?php wp_body_open(); ?>
<?php if (have_posts()) : while (have_posts()) : the_post(); the_content(); endwhile;
else: ?><main><h1>Page not recovered</h1><p>This page needs to be rebuilt.</p></main><?php endif; ?>
<?php wp_footer(); ?></body></html>
