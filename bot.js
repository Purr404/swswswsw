// Discord bot example using buttons
const { ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

// Create buttons for troop type selection
const row = new ActionRowBuilder()
    .addComponents(
        new ButtonBuilder()
            .setCustomId('horde')
            .setLabel('Horde')
            .setStyle(ButtonStyle.Primary)
            .setEmoji('⚔'),
        new ButtonBuilder()
            .setCustomId('league')
            .setLabel('League')
            .setStyle(ButtonStyle.Primary)
            .setEmoji('🏅'),
        new ButtonBuilder()
            .setCustomId('nature')
            .setLabel('Nature')
            .setStyle(ButtonStyle.Primary)
            .setEmoji('🌿')
    );

// Send message with buttons
await interaction.reply({
    content: 'Please select your main troop type:',
    components: [row]
});
