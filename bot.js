const { Client, EmbedBuilder, ActionRowBuilder, StringSelectMenuBuilder } = require('discord.js');
const client = new Client({ intents: 3276799 });

client.once('ready', async () => {
    console.log('✅ Bot ready');
    const channel = client.channels.cache.find(c => c.name === 'get-roles');
    
    // === MESSAGE 1 ===
    const embed1 = new EmbedBuilder()
        .setTitle('Channels & Roles')
        .setDescription('```\nCustomize    All Channels\n```\n\n**Customization Questions**\nAnswer questions to get access to more channels and roles.')
        .setColor(0x2f3136)
        .addFields({
            name: "What's your favorite set? *",
            value: '**Deluxe ex**\n\nYou will receive the @Deluxe ex role.'
        });
    
    const menu1 = new StringSelectMenuBuilder()
        .setCustomId('set')
        .setPlaceholder('Choose set...')
        .addOptions(
            { label: 'Deluxe ex', value: 'deluxe', emoji: '🎮' },
            { label: 'Basic', value: 'basic', emoji: '🔰' },
            { label: 'Premium', value: 'premium', emoji: '💎' }
        );
    
    await channel.send({ embeds: [embed1], components: [new ActionRowBuilder().addComponents(menu1)] });
    
    // === MESSAGE 2 ===
    const embed2 = new EmbedBuilder()
        .setColor(0x2f3136)
        .addFields({
            name: 'Would you like ping notifications?',
            value: '✅ **Announcements**\n□ **Tournaments**\n□ **Giveaways**\n\nYou will receive the @Announcements, @Tournaments, and 1 other role.'
        });
    
    const menu2 = new StringSelectMenuBuilder()
        .setCustomId('notifications')
        .setPlaceholder('Select notifications...')
        .setMinValues(0).setMaxValues(3)
        .addOptions(
            { label: 'Announcements', value: 'announcements', emoji: '📢' },
            { label: 'Tournaments', value: 'tournaments', emoji: '🏆' },
            { label: 'Giveaways', value: 'giveaways', emoji: '🎁' }
        );
    
    await channel.send({ embeds: [embed2], components: [new ActionRowBuilder().addComponents(menu2)] });
    
    // === MESSAGE 3 ===
    const embed3 = new EmbedBuilder()
        .setColor(0x2f3136)
        .addFields({
            name: 'Select main troop type *',
            value: '⚪ **⚔ Horde**\n🔘 **🏅 League**\n⚪ **🌿 Nature**\n\nYou will receive the @League role.'
        });
    
    const menu3 = new StringSelectMenuBuilder()
        .setCustomId('troop')
        .setPlaceholder('Select troop...')
        .addOptions(
            { label: 'Horde', value: 'horde', emoji: '⚔️' },
            { label: 'League', value: 'league', emoji: '🏅' },
            { label: 'Nature', value: 'nature', emoji: '🌿' }
        );
    
    await channel.send({ embeds: [embed3], components: [new ActionRowBuilder().addComponents(menu3)] });
});

client.login(process.env.TOKEN);