<?php
// Run with wp eval-file /rebuild/wordpress/import.php on a NEW staging database.
if (!defined('WP_CLI') || !WP_CLI) { exit; }
if (!in_array(wp_get_environment_type(), ['local','development','staging'], true)) { WP_CLI::error('Recovery imports require a local, development or staging environment.'); }
$refresh = in_array('refresh', $args ?? [], true);
$bundle = json_decode(file_get_contents('/rebuild/generated/pages.json'), true);
if (!is_array($bundle)) { WP_CLI::error('Generate the recovery bundle first.'); }
kses_remove_filters(); // Import sanitized, owner-requested captured HTML without reformatting it.
$ids = [];
$written = [];
$skipped = 0;
foreach ($bundle as $page) {
    $existing = get_posts(['post_type'=>'page','post_status'=>'any','meta_key'=>'_labg_source_url','meta_value'=>$page['url'],'numberposts'=>1]);
    if ($existing && !$refresh) {
        $ids[$page['path']] = $existing[0]->ID;
        $skipped++;
        continue;
    }
    $data = ['post_type'=>'page','post_status'=>'publish','post_title'=>$page['title'],'post_name'=>$page['slug'], 'post_content'=>str_replace('__LABG_ORIGIN__', home_url(), $page['body'])];
    if ($existing) { $data['ID']=$existing[0]->ID; }
    $id=wp_insert_post(wp_slash($data), true);
    if (is_wp_error($id)) { WP_CLI::error($id->get_error_message()); }
    update_post_meta($id,'_labg_source_url',$page['url']);
    update_post_meta($id,'_labg_head',wp_slash(str_replace('__LABG_ORIGIN__',home_url(),$page['head'])));
    update_post_meta($id,'_labg_body_attributes',wp_slash($page['body_attributes']));
    update_post_meta($id,'_labg_html_attributes',wp_slash($page['html_attributes']));
    $ids[$page['path']]=$id;
    $written[$id]=true;
}
// Assign parents only after all pages exist.
foreach ($bundle as $page) {
    if (!isset($written[$ids[$page['path']]])) { continue; }
    $parent=trim(dirname(trim($page['path'],'/')),'. /');
    if ($parent && isset($ids['/'.$parent.'/'])) { wp_update_post(['ID'=>$ids[$page['path']],'post_parent'=>$ids['/'.$parent.'/']]); }
}
if (isset($ids['/']) && isset($written[$ids['/']])) { update_option('show_on_front','page'); update_option('page_on_front',$ids['/']); }
if (!get_option('permalink_structure')) { update_option('permalink_structure','/%postname%/'); }
flush_rewrite_rules();
kses_init_filters();
WP_CLI::success(count($written).' pages imported; '.$skipped.' existing pages preserved.');
