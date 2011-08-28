
Ext.grid.feature.Grouping.override({
	/**
	 * Override the default getGroupRows implementation to add the column
	 * title and the rendered group value to the groupHeaderTpl data.
	 */
	getGroupRows: function(g) {
		
		var me = this,
			view = me.view,
			header = view.getHeaderCt(),
			store = view.store,
			record = g.children[0], // get first record in group
			group = me.callOverridden(arguments),
			grouper = me.getGroupField(),
			column,
			renderer,
			v;
		if (!Ext.isEmpty(grouper) && record) {
			// get column of groupfield
			column = header.down('[dataIndex=' + grouper + ']');
			// render the group value
			renderer = column.renderer;
			if (renderer) {
				v = header.prepareData(record[record.persistenceProperty], store.indexOf(record), record, view, view.ownerCt)[column.id];
			} else {
				v = group.name;
			}
			// apply column title and rendered group value for use in groupHeaderTpl
			Ext.apply(group, {
				header: column.text,
				renderedValue: v
			});
		}
		return group;
	}
});
