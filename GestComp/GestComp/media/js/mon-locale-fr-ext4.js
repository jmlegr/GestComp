/* correction des erreurs dans le fichier locale de extjs 4
 * 
 */
if(Ext.grid.feature.Grouping){
        Ext.apply(Ext.grid.feature.Grouping.prototype, {

            emptyGroupText : '(Aucun)',
            groupByText    : 'Grouper par ce champ',
            showGroupsText : 'Afficher par groupes'
        });
    }