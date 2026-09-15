<?php if (!get_post_meta(get_queried_object_id(), '_labg_source_url', true)) : ?>
<footer class="labg-native-footer"><?php echo esc_html(get_bloginfo('name')); ?></footer>
<?php endif; ?>
<?php wp_footer(); ?>
</body>
</html>
