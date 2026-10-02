/**
 * PauseBeforeBuy · comprehension test questionnaire
 * Creates the whole Google Form in your own Google account.
 *
 * How to run ｜ 运行方法:
 * 1. Go to https://script.google.com → New project ｜ 新建项目
 * 2. Delete everything in the editor, paste this whole file, click Save ｜ 删除编辑器里的内容，粘贴本文件，保存
 * 3. Choose the function "createPauseBeforeBuyForm" at the top, click Run ｜ 选择函数 createPauseBeforeBuyForm，点运行
 * 4. Approve the permission request (it only creates a form in your account) ｜ 授权（只会在你的账号里创建表单）
 * 5. Open "Execution log" to copy the form links ｜ 在执行日志中复制表单链接
 *
 * Question order and option wording match the scoring template
 * (PauseBeforeBuy_comprehension_scoring.xlsx). Do not reorder questions
 * or remove the English keywords from the options.
 * 题目顺序和选项措辞与评分模板一致，请不要调整顺序，也不要删掉选项中的英文关键词。
 */

var SITE_URL = 'https://judylou0117-stack.github.io/PauseBeforeBuy/';

function createPauseBeforeBuyForm() {
  var form = FormApp.create('PauseBeforeBuy · User study ｜ 用户测试');
  form.setDescription(
    'Thank you for helping test PauseBeforeBuy, a decision-support tool that shows the financial consequences of buying something in full, in instalments, or later.\n' +
    '感谢你参与 PauseBeforeBuy 的测试。这是一个展示购物时一次付清、分期付款或先存钱再买各自后果的决策辅助工具。\n\n' +
    '• About 8 minutes. Anonymous: no name or email is collected.\n' +
    '  大约 8 分钟。匿名：不收集姓名或邮箱。\n' +
    '• You will use a fictional scenario. Please do not enter your own financial details anywhere.\n' +
    '  你将使用一个虚构场景，请不要在任何地方填写你自己的真实财务数据。\n' +
    '• Please answer Part A BEFORE opening the website.\n' +
    '  请在打开网站之前先回答 Part A。'
  );
  form.setIsQuiz(true);
  form.setCollectEmail(false);
  form.setProgressBar(true);
  form.setShuffleQuestions(false);
  form.setAllowResponseEdits(false);
  form.setPublishingSummary(false);
  form.setConfirmationMessage(
    'Thank you! Please do not share the questions or your answers with other participants until everyone has finished.\n' +
    '谢谢！在所有人完成之前，请不要和其他参与者分享题目或你的答案。'
  );

  // ---------------------------------------------------------------- Part A (before using the tool)
  form.addSectionHeaderItem()
    .setTitle('Part A · Before using the tool ｜ 使用工具之前')
    .setHelpText('Answer from what you know now. Do not open the website yet. ｜ 按你现在的了解作答，先不要打开网站。');

  var a1 = form.addMultipleChoiceItem();
  a1.setTitle('A1. Have you ever used buy-now-pay-later or a credit-card instalment plan? ｜ 你用过先买后付或信用卡分期吗？')
    .setChoices([
      a1.createChoice('Yes 是'),
      a1.createChoice('No 否'),
      a1.createChoice('Not sure 不确定')
    ])
    .setRequired(true);

  var a2 = form.addMultipleChoiceItem();
  a2.setTitle('A2. A plan charges 0.6% per month for 12 months. Roughly what does it cost per year? ｜ 一个分期方案每月收 0.6%，分 12 期。它一年的成本大约是多少？')
    .setChoices([
      a2.createChoice('(a) about 0.6% 约 0.6%', false),
      a2.createChoice('(b) about 7% 约 7%', false),
      a2.createChoice('(c) about 14% 约 14%', true),
      a2.createChoice('(d) Not sure 不确定', false)
    ])
    .setPoints(1)
    .setRequired(true);

  // ---------------------------------------------------------------- Part B + C (use the tool, then answer)
  form.addPageBreakItem()
    .setTitle('Part B · Use PauseBeforeBuy ｜ 使用 PauseBeforeBuy')
    .setHelpText(
      'Open the website in a NEW TAB: ' + SITE_URL + '\n' +
      '在新标签页中打开网站：' + SITE_URL + '\n\n' +
      'Your fictional scenario ｜ 你的虚构场景:\n' +
      '• Laptop price 笔记本电脑价格: SGD 6,000\n' +
      '• Instalment plan 分期期数: 12 months 个月\n' +
      '• Fee 手续费: 0.6% per instalment 每期 → choose “A fee on every instalment 每期收取手续费” and type 0.6\n' +
      '• Monthly take-home income 每月税后收入: SGD 3,500\n' +
      '• Cash savings 现金储蓄: SGD 5,000\n' +
      '• Essential spending 每月必要支出: SGD 2,200 a month\n' +
      '• Existing repayments 每月已有还款: SGD 300 a month\n\n' +
      'Keep the results page open and use it to answer Part C. You may choose English or Chinese on the website.\n' +
      '保持结果页打开，用它回答 Part C。网站可以选择中文或英文。'
    );

  form.addSectionHeaderItem()
    .setTitle('Part C · Using the results page ｜ 看结果页作答')
    .setHelpText('Type numbers only, without “SGD” or “%”. ｜ 只填数字，不要写 SGD 或 %。');

  addNumberQuestion(form, 'C1. If you pay in instalments, how much do you pay in total (SGD)? ｜ 如果分期付款，你总共要付多少钱（新元）？');
  addNumberQuestion(form, 'C2. How much would you pay each month (SGD)? ｜ 每月要还多少钱（新元）？');
  addNumberQuestion(form, 'C3. During the instalment plan, how many months of essential spending could your savings cover? ｜ 分期期间，你的储蓄可以支撑几个月的必要开支？');

  var c4 = form.addMultipleChoiceItem();
  c4.setTitle('C4. Which option is NOT possible with your current savings? ｜ 以你目前的储蓄，哪个方案不可行？')
    .setChoices([
      c4.createChoice('(a) Pay in full 一次付清', true),
      c4.createChoice('(b) Pay in instalments 分期付款', false),
      c4.createChoice('(c) Wait and save 先存钱再买', false),
      c4.createChoice('(d) All are possible 都可行', false)
    ])
    .setPoints(1)
    .setRequired(true);

  var c5 = form.addMultipleChoiceItem();
  c5.setTitle('C5. What is the main risk of paying in instalments? ｜ 分期付款的主要风险是什么？')
    .setChoices([
      c5.createChoice('(a) You cannot afford the monthly payment 负担不起月供', false),
      c5.createChoice('(b) Your emergency savings fall below the 3-month target, and you pay extra to borrow 应急储蓄低于 3 个月目标，还要多付借贷成本', true),
      c5.createChoice('(c) The price of the laptop will go up 电脑会涨价', false),
      c5.createChoice('(d) There is no real risk 没有实际风险', false)
    ])
    .setPoints(1)
    .setRequired(true);

  addNumberQuestion(form, 'C6. What is the true yearly cost of the instalment plan (%)? ｜ 这个分期方案真实的年化成本是多少（%）？');

  // ---------------------------------------------------------------- Part D + E (experience)
  form.addPageBreakItem()
    .setTitle('Part D · Your experience ｜ 使用体验')
    .setHelpText('1 = strongly disagree, 5 = strongly agree ｜ 1 = 非常不同意，5 = 非常同意');

  addScale(form, 'D1. The results were easy to understand. ｜ 结果很容易理解。');
  addScale(form, 'D2. I trusted the numbers shown. ｜ 我信任页面上显示的数字。');
  addScale(form, 'D3. The pause made me think again about the purchase. ｜ 暂停的时刻让我重新考虑了这次购买。');

  var d4 = form.addMultipleChoiceItem();
  d4.setTitle('D4. Did the tool tell you which option to choose? ｜ 这个工具有没有告诉你应该选哪个方案？')
    .setChoices([
      d4.createChoice('Yes 有'),
      d4.createChoice('No 没有'),
      d4.createChoice('Not sure 不确定')
    ])
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('E1. Was anything confusing or missing? (optional) ｜ 有没有让你困惑或觉得缺少的地方？（选填）')
    .setRequired(false);

  Logger.log('Share this link with participants ｜ 发给参与者的链接: ' + form.getPublishedUrl());
  Logger.log('Edit the form here ｜ 编辑表单: ' + form.getEditUrl());
}

function addNumberQuestion(form, title) {
  var validation = FormApp.createTextValidation()
    .setHelpText('Please enter a number only, e.g. 1234 or 12.5 ｜ 请只填数字，例如 1234 或 12.5')
    .requireNumber()
    .build();
  return form.addTextItem().setTitle(title).setValidation(validation).setRequired(true);
}

function addScale(form, title) {
  return form.addScaleItem()
    .setTitle(title)
    .setBounds(1, 5)
    .setLabels('Strongly disagree 非常不同意', 'Strongly agree 非常同意')
    .setRequired(true);
}
