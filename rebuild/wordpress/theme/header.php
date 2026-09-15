<?php
$labg_recovered = (bool) get_post_meta(get_queried_object_id(), '_labg_source_url', true);
$labg_body = labg_recovery_attributes('_labg_body_attributes');
$labg_html = labg_recovery_attributes('_labg_html_attributes');
?><!doctype html>
<html <?php language_attributes(); ?> class="<?php echo esc_attr($labg_html['class'] ?? ''); ?>">
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php if ($labg_recovered) { echo get_post_meta(get_queried_object_id(), '_labg_head', true); } ?>
<?php wp_head(); ?>
</head>
<body id="<?php echo esc_attr($labg_body['id'] ?? 'top'); ?>" <?php body_class(($labg_body['class'] ?? '') . ($labg_recovered ? ' labg-recovered' : ' labg-native')); ?>>
<?php wp_body_open(); ?>
<?php if (!$labg_recovered) : ?>
<a class="labg-skip-link" href="#labg-content">Skip to content</a>
<header class="labg-native-header">
<a href="<?php echo esc_url(home_url('/')); ?>"><?php bloginfo('name'); ?></a>
<?php wp_nav_menu(['theme_location'=>'primary','container'=>'nav','container_aria_label'=>'Primary navigation','fallback_cb'=>false]); ?>
</header>
<?php endif; ?>
