<?php get_header(); ?>
<?php if (have_posts()) : while (have_posts()) : the_post(); ?>
    <?php if (get_post_meta(get_the_ID(), '_labg_source_url', true)) : ?>
        <?php the_content(); ?>
    <?php else : ?>
        <main id="labg-content" class="labg-native-content">
            <h1><?php the_title(); ?></h1>
            <?php the_content(); ?>
        </main>
    <?php endif; ?>
<?php endwhile; else : ?>
<main id="labg-content" class="labg-native-content"><h1>Page not found</h1><p>This address has not been recovered or created yet.</p><a href="<?php echo esc_url(home_url('/')); ?>">Return to the homepage</a></main>
<?php endif; ?>
<?php get_footer(); ?>
