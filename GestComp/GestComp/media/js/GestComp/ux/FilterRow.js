

Ext.define('Ext.ux.grid.FilterRow', {
			extend				: 'Ext.util.Observable',

			init				: function(grid) {
				this.grid = grid;
				this.applyTemplate();

				// when Ext grid state restored (untested)
				grid.on("staterestore", this.resetFilterRow, this);

				// when column width programmatically changed
				grid.headerCt.on("columnresize", this.resizeFilterField, this);

				grid.headerCt.on("columnmove", this.resetFilterRow, this);
				grid.headerCt.on("columnshow", this.resetFilterRow, this);
				grid.headerCt.on("columnhide", this.resetFilterRow, this);

				grid.horizontalScroller.on('bodyscroll',
						this.scrollFilterField, this
				);
			},

			applyTemplate		: function() {
				var searchItems = [];
				this.eachColumn(function(col) {
							var filterDivId = this.getFilterDivId(col.id);

							if (!col.xfilterField) {

								if (col.nofilter
										|| col.isCheckerHd != undefined) {
									col.xfilter = {};
								} else if (!col.xfilter) {
									col.xfilter = {};
									col.xfilter.xtype = 'textfield';
								}
								col.xfilter = Ext.apply({
											id				: filterDivId,
											hidden			: col.hidden,
											xtype			: 'component',
											baseCls			: "xfilter-row",
											width			: col.width - 2,
											enableKeyEvents	: true,
											style			: {
												margin	: '1px 1px 1px 1px'
											},
											hideLabel		: true
										}, col.xfilter);

								col.xfilterField = Ext.ComponentManager
										.create(col.xfilter);

							} else {
								if (col.hidden != col.xfilterField.hidden) {
									col.xfilterField.setVisible(!col.hidden);
								}
							}

							if (col.xfilterField.xtype == 'combo') {
								col.xfilterField.on("select", this.onSelect,
										this
								);
							} else if (col.xfilterField.xtype == 'datefield') {
								col.xfilterField.on("change", this.onChange,
										this
								);
							}

							col.xfilterField
									.on("keydown", this.onKeyDown, this);

							searchItems.push(col.xfilterField);
						});

				if (searchItems.length > 0) {
					this.grid.addDocked(this.dockedFilter = Ext.create(
							'Ext.container.Container', {
								id		: this.grid.id + 'docked-filter',
								weight	: 100,
								dock	: 'top',
								border	: false,
								baseCls	: Ext.baseCSSPrefix + 'grid-header-ct',
								items	: searchItems,
								layout	: {
									type	: 'hbox'
								}
							}
					));
				}
			},

			onSelect			: function(field, value, option) {
				if (!this.onChangeTask) {
					this.onChangeTask = new Ext.util.DelayedTask(function() {
								this.storeSearch();
							}, this);
				}

				this.onChangeTask.delay(1000);
			},

			onChange			: function(field, newValue, oldValue) {

				if (!this.onChangeTask) {
					this.onChangeTask = new Ext.util.DelayedTask(function() {
								this.storeSearch();
							}, this);
				}

				this.onChangeTask.delay(1000);

			},

			onKeyDown			: function(field, e) {
				if (e.getKey() == e.ENTER) {
					this.storeSearch();
				}
			},

			getSearchValues		: function() {
				var values = {};
				this.eachColumn(function(col) {
							if (col.xfilterField
									&& col.xfilterField.xtype != 'component') {
								values[col.dataIndex] = col.xfilterField
										.getValue();
							}
						});
				return values;
			},

			storeSearch			: function() {
				if (!this.grid.store.proxy.extraParams) {
					this.grid.store.proxy.extraParams = {};
				}
				this.grid.store.proxy.extraParams.search = this
						.getSearchValues();
				this.grid.store.currentPage = 1;
				this.grid.store.load();
			},

			resetFilterRow		: function() {
				this.grid.removeDocked(this.grid.id + 'docked-filter', true);
				delete this.dockedFilter;

				// This is because of the reconfigure
				var dockedFilter = document.getElementById(this.grid.id
						+ 'docked-filter');
				if (dockedFilter) {
					dockedFilter.parentNode.removeChild(dockedFilter);
				}

				this.applyTemplate();
			},

			resizeFilterField	: function(headerCt, column, newColumnWidth) {
				var editor;
				if (!column.xfilterField) {
					// This is because of the reconfigure
					this.resetFilterRow();
					editor = this.grid.headerCt.items.findBy(function(item) {
								return item.dataIndex == column.dataIndex;
							}).xfilterField;
				} else {
					editor = column.xfilterField;
				}

				if (editor) {
					editor.setWidth(newColumnWidth - 2);
				}
			},

			scrollFilterField	: function(e, target) {
				var width = this.grid.headerCt.el.dom.firstChild.style.width;
				this.dockedFilter.el.dom.firstChild.style.width = width;
				this.dockedFilter.el.dom.scrollLeft = target.scrollLeft;
			},

			// Returns HTML ID of element containing filter div
			getFilterDivId		: function(columnId) {
				return this.grid.id + '-filter-' + columnId;
			},

			// Iterates over each column that has filter
			eachFilterColumn	: function(func) {
				this.eachColumn(function(col, i) {
							if (col.xfilterField) {
								func.call(this, col, i);
							}
						});
			},

			// Iterates over each column in column config array
			eachColumn			: function(func) {
				Ext.each(this.grid.columns, func, this);
			}
		});