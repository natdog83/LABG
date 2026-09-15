<?php
add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    register_nav_menus(['primary' => 'Primary navigation']);
});
add_action('wp', function () {
    if (get_post_meta(get_queried_object_id(), '_labg_source_url', true)) {
        remove_filter('the_content', 'wpautop');
        remove_filter('the_content', 'wptexturize');
    }
});
// Retain captured URLs even when their former event/post type is not installed yet.
add_action('parse_request', function ($wp) {
    if (is_admin() || !$wp->request) { return; }
    $source='https://labrewersguild.org/'.trim($wp->request,'/').'/';
    $matches=get_posts(['post_type'=>'page','post_status'=>'publish','meta_key'=>'_labg_source_url','meta_value'=>$source,'numberposts'=>1,'fields'=>'ids']);
    if ($matches) { $wp->query_vars=['page_id'=>$matches[0]]; }
});
add_filter('page_link', function ($link, $id) {
    $source=get_post_meta($id,'_labg_source_url',true);
    return $source ? home_url(wp_parse_url($source,PHP_URL_PATH)) : $link;
},10,2);

/** Keep the original styling classes without printing arbitrary HTML attributes. */
function labg_recovery_attributes($key) {
    $raw = get_post_meta(get_queried_object_id(), $key, true);
    preg_match_all('/(?:^|\s)(id|class)\s*=\s*([\'"])(.*?)\2/s', $raw, $matches, PREG_SET_ORDER);
    $attributes = [];
    foreach ($matches as $match) { $attributes[$match[1]] = $match[3]; }
    return $attributes;
}
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('labg-recovery', get_stylesheet_uri(), [], wp_get_theme()->get('Version'));
});
