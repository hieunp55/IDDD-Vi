Có một cách tiếp cận mang lại cải tiến khả thi khi các DTO (Data Transfer Object - đối tượng truyền tải dữ liệu) trở nên không cần thiết. Cách này tập hợp toàn bộ các thể hiện (instance) của nhiều Aggregate (cụm đối tượng có tính toàn vẹn trong DDD) cho việc hiển thị khung nhìn (view) vào trong một Domain Payload Object [Vernon, DPO] (đối tượng tải trọng miền) duy nhất. DPO có động lực tương tự như DTO nhưng tận dụng được lợi thế của kiến trúc ứng dụng chạy trên một Virtual Machine (máy ảo) đơn lẻ. Nó được thiết kế để chứa các tham chiếu đến toàn bộ thể hiện Aggregate chứ không phải từng thuộc tính riêng lẻ. Các cụm thể hiện Aggregate có thể được luân chuyển giữa các tầng logic (tier hoặc layer) thông qua một đối tượng chứa Payload (tải trọng/dữ liệu thực tải) đơn giản. Application Service (xem mục 'Application Services') (dịch vụ ứng dụng) sử dụng các Repository (kho lưu trữ đối tượng miền) để truy xuất các thể hiện Aggregate cần thiết, sau đó khởi tạo DPO để nắm giữ tham chiếu tới từng thể hiện đó. Các thành phần ở tầng Presentation (hiển thị / trình diễn) sẽ yêu cầu đối tượng DPO cung cấp các tham chiếu thể hiện Aggregate, rồi sau đó yêu cầu chính các Aggregate này cung cấp các thuộc tính có thể hiển thị.

## Cowboy Logic

LB: 'Nếu bạn chưa từng bị ngã ngựa, thì tức là bạn cưỡi chưa đủ lâu.'

> 💡 **Giải thích thêm:** "Cowboy Logic" và ngạn ngữ "Nếu bạn chưa từng ngã ngựa, bạn cưỡi chưa đủ lâu" là triết lý thực tế của giới cao bồi miền Tây nước Mỹ, hàm ý rằng khi làm việc thực tế với hệ thống phần mềm phức tạp, việc vấp phải sai sót, ngoại lệ hoặc sự cố biên là điều không thể tránh khỏi; người chưa từng gặp sự cố thường chỉ là do chưa trải nghiệm thực tế đủ lâu.  
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000568_e554bb9492e6172ff1754b9d956e7d8e3c141cd75225f55cf239a1dab5d3ef8a.png)

Cách tiếp cận này có ưu điểm là đơn giản hóa việc thiết kế các đối tượng dùng để luân chuyển các cụm dữ liệu giữa các tầng logic. Các DPO thường dễ thiết kế hơn nhiều và chiếm dụng bộ nhớ (memory footprint) nhỏ hơn. Vì dù sao các thể hiện Aggregate cũng bắt buộc phải được đọc vào bộ nhớ, nên chúng ta tận dụng luôn việc chúng đã tồn tại sẵn.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000569_8229e711e138d11dfcd96cbc6495e73989967b1773e4eb18cf123dcce250356f.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000570_c6252b95e2433b70dad6753fe9d2613987ed486e6b97527107680f1af4bddd0c.png)

Tuy nhiên, có một vài hệ quả tiêu cực tiềm ẩn cần cân nhắc. Do tính chất tương đồng với DTO, cách tiếp cận này cũng đòi hỏi các Aggregate phải cung cấp phương thức để đọc trạng thái của chúng. Để tránh việc giao diện người dùng (UI) bị phụ thuộc chặt chẽ (tight coupling) vào mô hình, chúng ta cũng có thể áp dụng các giải pháp như Mediator (mẫu thiết kế trung gian), Double-Dispatch (kỹ thuật phân phối kép), hoặc giao diện truy vấn trên Aggregate Root (gốc cụm đối tượng) – những kỹ thuật từng được đề xuất trước đó cho DTO Assembler.

Vẫn còn một tình huống khác cần xử lý. Do DPO nắm giữ các tham chiếu đến toàn bộ các thể hiện Aggregate, nên bất kỳ đối tượng hoặc tập hợp (collection) nào được nạp theo cơ chế lazy loading (nạp lười / trì hoãn nạp khi cần) đều chưa được phân giải (unresolved). Không có lý do gì để phải truy cập vào tất cả các thuộc tính Aggregate cần thiết chỉ để tạo ra Domain Payload Object. Do ngay cả các giao dịch (transaction) chỉ đọc (read-only) cũng thường được commit khi phương thức của Application Service kết thúc, bất kỳ thành phần hiển thị nào tham chiếu đến các đối tượng lazy-loaded chưa được phân giải sẽ gây ra ngoại lệ (exception). 3

Để xử lý triệt để các lazy load cần thiết, chúng ta có thể chọn chiến lược eager loading (nạp dữ liệu sớm / nạp ngay lập tức), hoặc có thể dùng một Domain Dependency Resolver [Vernon, DDR] (bộ phân giải phụ thuộc miền). Đây là một biến thể của Strategy [Gamma et al.] (mẫu thiết kế chiến lược), thường áp dụng một Strategy cho mỗi luồng use case. Mỗi Strategy sẽ ép buộc việc truy cập vào toàn bộ các thuộc tính lazy-loaded của Aggregate được sử dụng bởi luồng use case cụ thể đó. Việc ép buộc truy cập này diễn ra trước khi Application Service commit transaction và trả Domain Payload Object về cho client của nó. Strategy có thể được hard-code (viết mã cứng) để truy cập thủ công các thuộc tính lazy-loaded, hoặc có thể sử dụng một ngôn ngữ biểu thức (expression language) đơn giản mô tả cách thức điều hướng nội quan (introspectively) và phản xạ (reflectively) qua các thể hiện Aggregate. Bộ thu thập điều hướng dựa trên reflection này có ưu điểm là có thể tác động được lên cả các thuộc tính ẩn (hidden attributes). Dù vậy, bạn có thể sẽ cảm thấy thoải mái hơn khi tùy biến truy vấn để fetch sớm (eager fetch) các đối tượng vốn thường được lazy load, nếu tùy chọn đó khả dụng.

## State Representations of Aggregate Instances

Nếu ứng dụng của bạn cung cấp các tài nguyên dựa trên REST (Representational State Transfer - kiến trúc truyền trạng thái đại diện) như đã thảo luận trong chương REST (4), chúng sẽ cần tạo ra các biểu diễn trạng thái (state representation) của các đối tượng miền cho client. Việc tạo ra các biểu diễn dựa trên use case chứ không phải dựa trên các thể hiện Aggregate là điều tối quan trọng. Điều này xuất phát từ động lực rất tương đồng với DTO – vốn cũng được tinh chỉnh cho các use case. Tuy nhiên, sẽ chính xác hơn nếu xem tập hợp các tài nguyên RESTful như một mô hình độc lập thực thụ – một View Model hoặc Presentation Model [Fowler, PM] (mô hình hiển thị / trình bày). Hãy cưỡng lại cám dỗ tạo ra các biểu diễn phản chiếu 1-1 trạng thái của các Aggregate trong mô hình miền, có thể đi kèm các liên kết để điều hướng tới trạng thái sâu hơn. Nếu không, các client của bạn sẽ buộc phải hiểu cặn kẽ cả mô hình miền lẫn bản thân các Aggregate. Khi đó, client sẽ phải nắm rõ mọi ngóc ngách tinh tế trong các hành vi và sự chuyển đổi trạng thái, và bạn sẽ đánh mất toàn bộ lợi ích của tính trừu tượng hóa (abstraction).

3. Một số người thích dùng Open Session In View (OSIV - kỹ thuật mở session tầng hiển thị) để kiểm soát transaction ở cấp độ request-response (yêu cầu - phản hồi), tức là ở vị trí rất cao trên giao diện người dùng. Vì nhiều lý do khác nhau, tôi coi OSIV là có hại, nhưng YMMV ('Your Mileage May Vary').

> 💡 **Giải thích thêm:** Thành ngữ "Your Mileage May Vary" (YMMV) vốn bắt nguồn từ các quảng cáo xe hơi tại Mỹ cảnh báo rằng mức tiêu hao nhiên liệu thực tế có thể khác nhau tùy người lái. Trong giới kỹ thuật phần mềm, câu này mang hàm ý: "đây là nhận định mang tính trải nghiệm cá nhân của tác giả, còn trong thực tế dự án của bạn thì hiệu quả có thể sẽ khác nhau tùy bối cảnh".  
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

## Use Case Optimal Repository Queries

Thay vì phải đọc nhiều thể hiện Aggregate hoàn chỉnh thuộc các kiểu khác nhau rồi dùng mã lập trình để gom chúng vào một container duy nhất (DTO hoặc DPO), bạn có thể sử dụng giải pháp gọi là truy vấn tối ưu theo use case (use case optimal query). Đây là cách bạn thiết kế Repository của mình với các phương thức truy vấn tìm kiếm (finder method) có khả năng tổng hợp một đối tượng tùy chỉnh dưới dạng một tập cha (superset) chứa dữ liệu từ một hoặc nhiều thể hiện Aggregate. Truy vấn sẽ tự động đưa kết quả vào một Value Object (6) (đối tượng giá trị) được thiết kế chuyên biệt để đáp ứng nhu cầu của use case đó. Bạn thiết kế một Value Object chứ không phải DTO, bởi vì truy vấn này mang tính đặc thù của miền (domain-specific), chứ không mang tính đặc thù của ứng dụng (application-specific như DTO). Value Object tùy chỉnh tối ưu theo use case này sau đó sẽ được bộ hiển thị khung nhìn (view renderer) sử dụng trực tiếp.

Cách tiếp cận truy vấn tối ưu theo use case có động lực tương tự như CQRS (4) (Command Query Responsibility Segregation - phân tách trách nhiệm dòng lệnh và truy vấn). Tuy nhiên, truy vấn tối ưu theo use case sử dụng một Repository thao tác trên kho lưu trữ dữ liệu bền vững (persistence store) hợp nhất của mô hình miền, thay vì dùng một truy vấn cơ sở dữ liệu thô (chẳng hạn như SQL) thao tác trên một kho lưu trữ truy vấn/đọc (query/read store) riêng biệt. Để hiểu rõ sự đánh đổi giữa cách tiếp cận này so với CQRS, hãy xem thảo luận liên quan trong phần Repositories (12). Dẫu vậy, một khi bạn đã bắt đầu đi theo con đường truy vấn tối ưu theo use case này, bạn đã ở rất gần với CQRS đến mức có lẽ việc chuyển hẳn sang hướng CQRS sẽ đáng giá hơn.

## Dealing with Multiple, Disparate Clients

Bạn sẽ làm gì nếu ứng dụng của mình bắt buộc phải hỗ trợ nhiều loại client khác biệt nhau? Danh sách này có thể bao gồm RIA (Rich Internet Application - ứng dụng internet đa tính năng), một thick client (ứng dụng client đồ họa dày), các dịch vụ nền tảng REST, và cả cơ chế messaging (truyền thông điệp). Bạn có thể cũng sẽ xem các bộ điều khiển kiểm thử (test driver) khác nhau như các loại client riêng biệt. Như sẽ được thảo luận chi tiết hơn ở phần sau, bạn có thể thiết kế các Application Service của mình để tiếp nhận một Data Transformer (bộ chuyển đổi dữ liệu), trong đó mỗi client sẽ chỉ định cụ thể loại Data Transformer tương ứng. Application Service sau đó sẽ thực hiện double-dispatch trên tham số Data Transformer, từ đó tạo ra định dạng dữ liệu theo yêu cầu. Dưới đây là cách mà phía giao diện người dùng có thể hiển thị cho một client nền REST:

```java
...
CalendarWeekData calendarWeekData =
    calendarAppService.calendarWeek(date, new CalendarWeekXMLDataTransformer());

Response response =
    Response.ok(calendarWeekData.value())
        .cacheControl(this.cacheControlFor(30))
        .build();

return response;

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000571_f099e576693bd497e7c98d2be192e526a74be5abf81ac5316f7a94022ad95bee.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000572_51cbeb5c0690c3f296e8af32bd772400cf4f4d85355a242926e9c42eee456820.png)

Phương thức `calendarWeek()` của `CalendarApplicationService` tiếp nhận một `Date` nằm trong một tuần nhất định và một bản cài đặt của interface `CalendarWeekDataTransformer`. Lớp triển khai được chọn là `CalendarWeekXMLDataTransformer`, có nhiệm vụ tạo ra một tài liệu XML đóng vai trò là biểu diễn trạng thái của `CalendarWeekData`. Phương thức `value()` trên `CalendarWeekData` sẽ trả về kiểu dữ liệu ưu tiên của định dạng dữ liệu đã cho, trong trường hợp này là một `String` chứa tài liệu XML.

Phải thừa nhận rằng ví dụ này sẽ tốt hơn nếu thể hiện của Data Transformer được dependency injected (tiêm phụ thuộc). Ở đây nó được hard-code nhằm giúp ví dụ trở nên dễ hiểu hơn.

Trong số các lớp triển khai tiềm năng của `CalendarWeekDataTransformer`, chẳng hạn có thể bao gồm:

* CalendarWeekCSVDataTransformer
* CalendarWeekDPODataTransformer
* CalendarWeekDTODataTransformer
* CalendarWeekJSONDataTransformer
* CalendarWeekTextDataTransformer
* CalendarWeekXMLDataTransformer

Còn một cách tiếp cận khả thi khác để trừu tượng hóa các kiểu đầu ra của ứng dụng tới các client khác nhau mà tôi sẽ thảo luận sau trong mục 'Application Services.'

## Rendition Adapters and Handling User Edits

Khi bạn đã có dữ liệu miền và dữ liệu đó cần được người dùng xem cũng như chỉnh sửa, sẽ có những pattern giúp bạn phân tách trách nhiệm rõ ràng. Một lần nữa, có quá nhiều framework ngoài kia cùng vô số cách xử lý tương ứng, đến mức không thể đề xuất một phương pháp chắc chắn hiệu quả cho tất cả. Với một số framework giao diện người dùng, bạn bắt buộc phải tuân theo các pattern cụ thể mà chúng hỗ trợ. Đôi khi những pattern đó rất tốt, nhưng đôi khi lại không tốt lắm. Với các framework khác, bạn có thể linh hoạt hơn đôi chút.

Dù dữ liệu miền của bạn được cung cấp từ Application Service theo cách nào đi chăng nữa — qua DTO, DPO, hay các biểu diễn trạng thái — và bất kể bạn sử dụng presentation framework nào, bạn đều có thể hưởng lợi từ Presentation Model. 4 Mục tiêu của nó là phân tách trách nhiệm giữa tầng hiển thị và view. Mặc dù có thể làm cho nó hoạt động được với các ứng dụng Web 1.0, tôi cho rằng thế mạnh của nó nghiêng nhiều hơn về các ứng dụng Web 2.0 RIA hoặc những ứng dụng có client trên desktop, như đã mô tả trong phân loại thứ hai và thứ ba được liệt kê trước đó.

4. Xem thêm Model-View-Presenter [Dolphin], mà [Fowler, PM] gọi là Supervising Controller và Passive View.

Khi sử dụng pattern này, chúng ta muốn làm cho các view trở nên thụ động (passive), tức là chúng chỉ quản lý việc hiển thị dữ liệu cùng các điều khiển giao diện người dùng (UI controls) và hầu như không làm gì khác. Có hai cách để render (kết xuất) view:

1. Các view tự render dựa trên Presentation Model. Tôi nghĩ đây là cách tự nhiên hơn và loại bỏ sự phụ thuộc từ Presentation Model vào view.
2. Các view được render bởi Presentation Model. Cách này có lợi thế về mặt kiểm thử nhưng lại đòi hỏi Presentation Model phải gắn kết (couple) với view.

Presentation Model đóng vai trò như một Adapter [Gamma et al.] (mẫu thiết kế chuyển đổi/tiếp hợp). Nó che giấu các chi tiết của mô hình miền bằng cách cung cấp các thuộc tính và hành vi được thiết kế theo đúng nhu cầu của view. Điều này đồng nghĩa với việc nó không đơn thuần chỉ là một lớp vỏ mỏng manh (thin veneer) bọc quanh các thuộc tính của đối tượng miền hay DTO. Nó có nghĩa là các quyết định được đưa ra ngay bên trong Adapter dựa trên trạng thái của mô hình khi áp dụng vào view. Ví dụ, việc kích hoạt một điều khiển cụ thể trên view có thể không có mối quan hệ trực tiếp với bất kỳ thuộc tính đơn lẻ nào của mô hình miền, nhưng vẫn có thể được suy ra từ một hoặc nhiều thuộc tính như vậy. Thay vì yêu cầu mô hình miền phải hỗ trợ cụ thể các thuộc tính cần thiết cho view, trách nhiệm của Presentation Model là suy diễn các chỉ số và thuộc tính đặc thù cho view từ trạng thái của mô hình miền.

Một lợi ích khác, dù có phần tinh tế hơn, của việc sử dụng Presentation Model là nó có thể chuyển đổi các Aggregate không hỗ trợ giao diện JavaBean với các phương thức getter sang các framework giao diện người dùng vốn bắt buộc phải có getter. Rất nhiều, nếu không muốn nói là tất cả, các Web framework nền Java đều yêu cầu các đối tượng phải cung cấp các getter công khai, chẳng hạn như `getSummary()` và `getStory()`, trong khi thiết kế của mô hình miền lại ưu tiên các biểu thức tự nhiên, thông suốt (fluent expression) và đặc thù cho miền, phản ánh chặt chẽ Ubiquitous Language (1) (ngôn ngữ chung). Sự khác biệt có thể đơn giản chỉ là giữa `summary()` và `story()` so với các getter, nhưng lại tạo ra sự bất tương thích trở kháng (impedance mismatch) với framework giao diện người dùng. Tuy nhiên, Presentation Model có thể được dùng để dễ dàng chuyển đổi `summary()` thành `getSummary()` và `story()` thành `getStory()`, loại bỏ sự căng thẳng giữa mô hình và view:

```java
public class BacklogItemPresentationModel extends AbstractPresentationModel {
    private BacklogItem backlogItem;

    public BacklogItemPresentationModel(BacklogItem aBacklogItem) {
        super();
        this.backlogItem = backlogItem;
    }

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000573_a6883d379f29a1e6ed6ad7ca8ffc8415c3359a55a0a85dc126fa0892167b7d1c.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000574_b1e481bda89b70c21cc7d5d70f1a543c9ad34af9a669659d6561147db4feaab3.png)

```java
    public String getSummary() {
        return this.backlogItem.summary();
    }

    public String getStory() {
        return this.backlogItem.story();
    }
    ...
}

```

Dĩ nhiên, một Presentation Model có thể chuyển đổi qua lại giữa bất kỳ cách tiếp cận nào đã được thảo luận trước đó, bao gồm việc sử dụng DTO hoặc DPO, hoặc sử dụng một Mediator để qua đó trạng thái nội bộ của Aggregate được công khai ra ngoài.

Ngoài ra, các chỉnh sửa do người dùng thực hiện cũng được theo dõi bởi Presentation Model. Đây không phải là trường hợp gán quá nhiều trách nhiệm lên Presentation Model, bởi vì bản chất nó được dùng để chuyển đổi theo cả hai chiều: từ model sang view và từ view về model.

Một điểm quan trọng cần lưu ý là Presentation Model không phải là một Facade [Gamma et al.] (mẫu thiết kế mặt tiền) cồng kềnh gánh vác tác vụ nặng nhọc (heavy-lifting) bao bọc lấy các Application Service hoặc mô hình miền. Đúng là một khi người dùng hoàn thành một tác vụ trên giao diện người dùng, họ thường sẽ kích hoạt một thao tác kiểu 'apply' (áp dụng) hoặc 'cancel' (hủy bỏ), hoặc lý tưởng hơn là một command (lệnh) tường minh. Điều này đòi hỏi Presentation Model phải phản ánh hành động của người dùng tới ứng dụng, về bản chất đóng vai trò như một Facade tối giản bao bọc quanh một Application Service:

```java
public class BacklogItemPresentationModel extends AbstractPresentationModel {
    private BacklogItem backlogItem;
    private BacklogItemEditTracker editTracker;
    // phần sau được tiêm vào (injected)
    private BacklogItemApplicationService backlogItemAppService;

    public BacklogItemPresentationModel(BacklogItem aBacklogItem) {
        super();
        this.backlogItem = backlogItem;
        this.editTracker = new BacklogItemEditTracker(aBacklogItem);
    }
    ...
    public void changeSummaryWithType() {
        this.backlogItemAppService
            .changeSummaryWithType(
                this.editTracker.summary(),
                this.editTracker.type());
    }
    ...
}

```

Người dùng nhấp vào một nút lệnh trên view khiến cho phương thức `changeSummaryWithType()` được gọi. Trách nhiệm của `BacklogItemPresentationModel` là tương tác với một Application Service để áp dụng các chỉnh sửa đã diễn ra trên `editTracker`. Không có đối tượng đứng ngoài nào khác chờ đợi để tiếp nhận các chỉnh sửa của người dùng và xử lý chúng cả. Do đó, chúng ta có thể nói rằng Presentation Model là một Facade tối giản đối với các Application Service thay mặt cho view, nhưng chỉ đơn thuần là vì `changeSummaryWithType()` là một giao diện cấp cao hơn giúp `BacklogItemApplicationService` trở nên dễ sử dụng hơn. Tuy nhiên, chúng ta sẽ không muốn thấy nhiều dòng code trong lớp Presentation Model quản lý chi tiết việc sử dụng Application Service, hoặc tệ hơn nữa là bản thân nó tự đóng vai trò như Application Service đối với mô hình miền. Điều đó sẽ vượt quá xa phạm vi trách nhiệm của Presentation Model. Thay vào đó, chúng ta muốn thấy một sự ủy thác (delegation) đơn giản tới một Facade phức tạp và đảm nhận nhiều tác vụ nặng hơn, chính là `BacklogItemApplicationService`.

Đây là một cách tiếp cận mạnh mẽ để điều phối giữa mô hình miền và UI. Thậm chí nó có thể nhận được sự ủng hộ của bạn như một pattern quản lý UI linh hoạt nhất. Dù vậy, khi sử dụng bất kỳ kỹ thuật quản lý view nào, chúng ta vẫn thường xuyên phải tương tác với API của các Application Service.

## Application Services

Trong một số trường hợp, giao diện người dùng của bạn sẽ tổng hợp nhiều Bounded Context (2) (ngữ cảnh giới hạn) bằng cách sử dụng các thành phần Presentation Model độc lập, tất cả được cấu thành trên một khung nhìn duy nhất. Cho dù giao diện người dùng của bạn render một mô hình đơn lẻ hay tổng hợp nhiều mô hình, rất có thể nó sẽ tương tác với các Application Service, vì vậy hãy cùng xem xét chúng ngay bây giờ.

Các Application Service là client trực tiếp của mô hình miền. Để nắm được các tùy chọn về vị trí logic của Application Service, hãy xem phần Architecture (4). Chúng chịu trách nhiệm điều phối tác vụ cho các luồng use case, mỗi phương thức dịch vụ tương ứng với một luồng. Khi sử dụng cơ sở dữ liệu tuân thủ ACID, các Application Service cũng kiểm soát các transaction, đảm bảo rằng các chuyển đổi trạng thái của mô hình được lưu trữ bền vững một cách nguyên tử (atomically). Tôi sẽ thảo luận ngắn gọn về việc kiểm soát transaction ở đây, nhưng hãy xem phần Repositories (12) để có góc nhìn rộng hơn. Vấn đề bảo mật (security) cũng thường được đảm nhiệm bởi các Application Service.

Sẽ là một sai lầm nếu coi Application Service cũng giống như Domain Service (7) (dịch vụ miền). Chúng hoàn toàn không giống nhau. Sự tương phản giữa chúng phải thật rõ ràng, điều sẽ được chứng minh cụ thể trong phần tiếp theo. Chúng ta nên cố gắng đưa toàn bộ logic nghiệp vụ miền (business domain logic) vào trong chính mô hình miền, cho dù đó là trong Aggregate, Value Object, hay Domain Service. Hãy giữ cho các Application Service luôn mỏng (thin), chỉ sử dụng chúng để điều phối các tác vụ trên mô hình.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000575_40fca54897b0d8e39137eb49764c4d5483f0d12096396ff9265964d81237082d.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000576_089dd30025463200d53e4de44fbcfe29daeb9db78ce68584342399eac2fc40ca.png)

## Sample Application Service

Chúng ta hãy cùng xem xét một phần interface và class triển khai mẫu cho một Application Service. Đây là dịch vụ cung cấp khả năng quản lý tác vụ use case cho các tenant (bên thuê) thuộc Identity and Access Context. Đây chỉ là một ví dụ mẫu và không nên coi là câu trả lời tuyệt đối duy nhất. Những sự đánh đổi sẽ lộ rõ.

Đầu tiên, hãy xem xét interface cơ bản:

```java
package com.saasovation.identityaccess.application;

public interface TenantIdentityService {
    public void activateTenant(TenantId aTenantId);
    public void deactivateTenant(TenantId aTenantId);

    public String offerLimitedRegistrationInvitation(
        TenantId aTenantId,
        Date aStartsOnDate,
        Date anUntilDate);

    public String offerOpenEndedRegistrationInvitation(
        TenantId aTenantId);

    public Tenant provisionTenant(
        String aTenantName,
        String aTenantDescription,
        boolean isActive,
        FullName anAdministratorName,
        EmailAddress anEmailAddress,
        PostalAddress aPostalAddress,
        Telephone aPrimaryTelephone,
        Telephone aSecondaryTelephone,
        String aTimeZone);

    public Tenant tenant(TenantId aTenantId);
    ...
}

```

Sáu phương thức của Application Service này được dùng để tạo hoặc cấp phát (provision) một tenant, kích hoạt và vô hiệu hóa một tenant hiện có, gửi lời mời đăng ký có giới hạn và không giới hạn thời gian tới những người dùng tương lai, cũng như truy vấn thông tin một tenant cụ thể.

Một số kiểu dữ liệu từ mô hình miền được sử dụng trực tiếp trong các chữ ký phương thức này. Điều đó đòi hỏi giao diện người dùng phải nhận biết các kiểu này và phụ thuộc vào chúng. Đôi khi các Application Service được thiết kế để che chắn hoàn toàn cho giao diện người dùng khỏi mọi kiến thức miền như vậy. Khi làm như vậy, các chữ ký phương thức của Application Service chỉ sử dụng các kiểu nguyên thủy (`int`, `long`, `double`), `String`, và có thể là DTO. Tuy nhiên, như một giải pháp thay thế cho các cách tiếp cận này, một phương án tốt hơn có thể là thiết kế các đối tượng Command [Gamma et al.] (mẫu thiết kế mệnh lệnh / đối tượng lệnh) để thay thế. Không nhất thiết có cách nào là đúng hay sai hoàn toàn. Nó chủ yếu phụ thuộc vào sở thích và mục tiêu của bạn. Cuốn sách này trình bày từng phong cách trên qua các ví dụ khác nhau.

Hãy cân nhắc các sự đánh đổi. Nếu bạn loại bỏ các kiểu dữ liệu từ mô hình, bạn tránh được sự phụ thuộc và gắn kết, nhưng bạn lại đánh mất khả năng kiểm tra kiểu mạnh (strong type checking) cùng các kiểm tra hợp lệ cơ bản (guard) mà bạn vốn có được miễn phí từ các kiểu Value Object. Nếu bạn không để lộ các đối tượng miền dưới dạng kiểu trả về, bạn sẽ cần phải cung cấp các DTO. Nếu cung cấp DTO, có thể sẽ xuất hiện sự phức tạp ngẫu sinh (accidental complexity) trong giải pháp của bạn do chi phí phụ trội từ các kiểu bổ sung. Thêm vào đó là chi phí bộ nhớ phụ trội đã đề cập trước đây trong các ứng dụng có lưu lượng truy cập cao, gây ra bởi các DTO có thể không cần thiết liên tục được tạo ra và thu gom rác (garbage collect).

Dĩ nhiên, nếu bạn để lộ các đối tượng miền cho các loại client khác biệt, từng loại client sẽ phải tự xử lý chúng một cách riêng biệt. Một lần nữa, sự gắn kết sẽ cao hơn và khi có càng nhiều loại client thì đây càng trở thành một vấn đề lớn hơn. Với thực tế đó, ít nhất một vài phương thức trong số này có thể được thiết kế tốt hơn để xử lý kiểu trả về. Như đã thảo luận trước đây, chúng ta có thể sử dụng các Data Transformer thay thế:

```java
package com.saasovation.identityaccess.application;

public interface TenantIdentityService {
    ...
    public TenantData provisionTenant(
        String aTenantName,
        String aTenantDescription,
        boolean isActive,
        FullName anAdministratorName,
        EmailAddress anEmailAddress,
        PostalAddress aPostalAddress,
        Telephone aPrimaryTelephone,
        Telephone aSecondaryTelephone,
        String aTimeZone,
        TenantDataTransformer aDataTransformer);

    public TenantData tenant(
        TenantId aTenantId,
        TenantDataTransformer aDataTransformer);
    ...
}

```

Hiện tại, tôi sẽ tiếp tục với việc để lộ các đối tượng miền cho client và giả định rằng chúng ta chỉ có một giao diện người dùng duy nhất chạy trên nền Web. Điều này sẽ giúp đơn giản hóa các ví dụ. Sau đó, tôi sẽ quay trở lại với cách tiếp cận Data Transformer.

Hãy xem xét cách mà interface của Application Service được triển khai. Việc nhìn vào một vài phương thức đơn giản hơn để triển khai nó sẽ giúp làm nổi bật một số điểm cơ bản. Lưu ý rằng có thể việc áp dụng Separated Interface [Fowler, P of EAA] (interface tách biệt) không mang lại lợi thế nào. Dưới đây là một ví dụ mà chúng ta sẽ chỉ cần định nghĩa interface cùng với class triển khai:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000577_11c810bc211d4a241c43fccea074ac44e00e4ac78068875ef243af5cabc58cb9.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000578_3db29ffd7c23835326eef2548124d0b1fd6d07e798d703a076e4aada5446c431.png)

```java
package com.saasovation.identityaccess.application;

public class TenantIdentityService {
    @Transactional
    public void activateTenant(TenantId aTenantId) {
        this.nonNullTenant(aTenantId).activate();
    }

    @Transactional
    public void deactivateTenant(TenantId aTenantId) {
        this.nonNullTenant(aTenantId).deactivate();
    }
    ...
    @Transactional(readOnly = true)
    public Tenant tenant(TenantId aTenantId) {
        Tenant tenant = this
            .tenantRepository()
            .tenantOfId(aTenantId);
        return tenant;
    }

    private Tenant nonNullTenant(TenantId aTenantId) {
        Tenant tenant = this.tenant(aTenantId);
        if (tenant == null) {
            throw new IllegalArgumentException("Tenant does not exist.");
        }
        return tenant;
    }
}

```

Một client yêu cầu vô hiệu hóa một `Tenant` hiện có bằng phương thức `deactivateTenant()`. Để tương tác với đối tượng `Tenant` thực tế, chúng ta cần truy xuất nó từ `Repository` thông qua `TenantId` của nó. Tại đây, chúng ta đã tạo một phương thức trợ giúp nội bộ có tên `nonNullTenant()`, bản thân phương thức này lại ủy thác cho `tenant()`. Phương thức trợ giúp này tồn tại nhằm phòng vệ trước các thể hiện `Tenant` không tồn tại, và nó được sử dụng bởi tất cả các phương thức dịch vụ cần lấy ra một `Tenant` hiện có.

Các phương thức `activateTenant()` và `deactivateTenant()` được đánh dấu là transaction ghi thông qua annotation `@Transactional` của Spring. Phương thức `tenant()` được đánh dấu là transaction chỉ đọc. Trong cả ba trường hợp, khi client lấy bean này thông qua Spring context của nó và gọi một phương thức dịch vụ, một transaction sẽ được bắt đầu. Khi phương thức kết thúc bằng việc trả về bình thường, transaction sẽ được commit. Tùy thuộc vào cấu hình, các exception được ném ra trong phạm vi phương thức sẽ khiến transaction bị rollback.

Nhưng làm thế nào để chúng ta ngăn chặn việc lạm dụng các phương thức này, chẳng hạn bởi một kẻ xâm nhập độc hại? Khi đề cập đến việc vô hiệu hóa hoặc tái kích hoạt một tenant, đây là một thao tác trên thực tế chỉ nên được cấp quyền cho người dùng được ủy quyền là nhân viên của SaaS Ovation. Điều tương tự cũng áp dụng cho việc cấp phát một tenant thuê bao mới.

Sẽ ra sao nếu chúng ta tận dụng một công cụ như Spring Security? Chúng ta có thể sử dụng một annotation khác là `@PreAuthorize`:

```java
public class TenantIdentityService {
    @Transactional
    @PreAuthorize("hasRole('SubscriberRepresentative')")
    public void activateTenant(TenantId aTenantId) {
        this.nonNullTenant(aTenantId).activate();
    }

    @Transactional
    @PreAuthorize("hasRole('SubscriberRepresentative')")
    public void deactivateTenant(TenantId aTenantId) {
        this.nonNullTenant(aTenantId).deactivate();
    }
    ...
    @Transactional
    @PreAuthorize("hasRole('SubscriberRepresentative')")
    public Tenant provisionTenant(
        String aTenantName,
        String aTenantDescription,
        boolean isActive,
        FullName anAdministratorName,
        EmailAddress anEmailAddress,
        PostalAddress aPostalAddress,
        Telephone aPrimaryTelephone,
        Telephone aSecondaryTelephone,
        String aTimeZone) {
        return this.tenantProvisioningService

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000579_1d2da959d8e1bf0b77039b9871c97e37dcde932eb9872b3f6971f46ccdd88f4c.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000580_36b4382d95c31e4ee2889abe95320a5efc384af13ae7975c27400904efc97ae2.png)

```java
            .provisionTenant(
                aTenantName,
                aTenantDescription,
                isActive,
                anAdministratorName,
                anEmailAddress,
                aPostalAddress,
                aPrimaryTelephone,
                aSecondaryTelephone,
                aTimeZone);
    }
    ...
}

```

Đây là cơ chế bảo mật khai báo ở cấp độ phương thức (declarative method-level security) và nó ngăn chặn người dùng không được phân quyền truy cập vào các Application Service. Dĩ nhiên, giao diện người dùng cũng sẽ được thiết kế để ẩn mọi lối điều hướng đến các tính năng như vậy nếu người dùng chưa được cấp quyền. Tuy nhiên, điều đó không thể ngăn chặn được kẻ tấn công nguy hiểm, nhưng việc khai báo bảo mật này thì sẽ ngăn chặn được.

Cơ chế bảo mật phương thức dạng khai báo này khác với những gì IdOvation đang cung cấp. Nhân viên của SaaSOvation sẽ đăng nhập vào IdOvation theo cách khác so với người dùng của tenant. Cụ thể, những người có vai trò đặc biệt là `SubscriberRepresentative` sẽ được phép thực thi các phương thức nhạy cảm này, và không một người dùng thuê bao nào được phép thực hiện. Đương nhiên, điều này sẽ đòi hỏi sự tích hợp giữa IdOvation và Spring Security.

Bây giờ, khi nhìn vào phần triển khai của `provisionTenant()`, chúng ta thấy rằng nó ủy thác việc xử lý cho một Domain Service. Điều này làm nổi bật sự khác biệt giữa hai loại dịch vụ, đặc biệt là khi chúng ta quan sát sâu hơn bên trong lớp miền `TenantProvisioningService`. Có một lượng đáng kể domain logic nằm trong Domain Service này, nhưng lại có rất ít trong Application Service. Hãy xem xét những gì Domain Service thực hiện (mặc dù tôi không đưa code ở đây):

1. Khởi tạo một Aggregate `Tenant` mới và thêm nó vào Repository tương ứng.
2. Chỉ định một quản trị viên mới cho `Tenant` mới này. Việc này bao gồm cả việc cấp vai trò Administrator cho `Tenant` mới và phát đi Event `TenantAdministratorRegistered`.
3. Phát đi Event `TenantProvisioned`.

Nếu Application Service làm nhiều hơn bước 1, chúng ta sẽ làm rò rỉ nghiêm trọng domain logic ra ngoài mô hình. Vì có thêm hai bước bổ sung không thuộc phạm vi trách nhiệm của Application Service, nên thay vào đó chúng ta đặt cả ba bước này vào bên trong Domain Service. Bằng cách sử dụng Domain Service, chúng ta đặt

'tiến trình có ý nghĩa quan trọng . . . vào bên trong miền' [Evans]. 5 Chúng ta cũng tuân thủ đúng định nghĩa về Application Service bằng cách quản lý transaction, bảo mật, và nhiệm vụ ủy thác tiến trình cấp phát tenant quan trọng này cho mô hình.

Nhưng hãy dành một chút thời gian để cân nhắc về sự phiền toái gây ra bởi danh sách tham số của `provisionTenant()`. Có tổng cộng 9 tham số, và con số đó có lẽ là hơi nhiều. Chúng ta có thể ngăn chặn tình huống này bằng cách thiết kế các đối tượng Command [Gamma et al.] đơn giản để thay thế: 'Đóng gói một yêu cầu dưới dạng một đối tượng, qua đó cho phép bạn tham số hóa các client với các yêu cầu khác nhau, xếp hàng đợi hoặc ghi nhật ký các yêu cầu, và hỗ trợ các thao tác có thể hoàn tác.' Nói cách khác, chúng ta có thể xem một đối tượng Command như một lời gọi phương thức đã được tuần tự hóa, và trong trường hợp của chúng ta, chúng ta quan tâm đến mọi thứ mà một Command có thể hỗ trợ ngoại trừ thao tác hoàn tác. Việc thiết kế một lớp Command đơn giản như sau:

```java
public class ProvisionTenantCommand {
    private String tenantName;
    private String tenantDescription;
    private boolean isActive;
    private String administratorFirstName;
    private String administratorLastName;
    private String emailAddress;
    private String primaryTelephone;
    private String secondaryTelephone;
    private String addressStreetAddress;
    private String addressCity;
    private String addressStateProvince;
    private String addressPostalCode;
    private String addressCountryCode;
    private String timeZone;

    public ProvisionTenantCommand(...) {
        ...
    }

    public ProvisionTenantCommand() {
        super();
    }

    public String getTenantName() {
        return tenantName;
    }

    public void setTenantName(String tenantName) {
        this.tenantName = tenantName;
    }
    ...
}

```

5. Xem Chương 7.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000581_2c777950f1aa3f0c68a7305ece829a6a525fc0f6efe10025e8ba26d7ba1333ff.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000582_9d77ba2482ffd0f1bba8bbf929a0d8efa9065c406b0f1bfd692e5546cfd44dc4.png)

`ProvisionTenantCommand` không sử dụng các đối tượng mô hình mà chỉ dùng các kiểu dữ liệu cơ bản. Nó có constructor nhiều tham số và cả constructor không tham số. Cùng với constructor không tham số, việc có các setter công khai cho phép Command được nạp dữ liệu bởi các bộ ánh xạ từ trường của form trên UI sang đối tượng (ví dụ: giả sử theo chuẩn JavaBean, hoặc các thuộc tính .NET CLR). Bạn có thể nghĩ Command tương tự như một DTO, nhưng thực sự nó mang nhiều ý nghĩa hơn thế. Vì đối tượng Command được đặt tên theo đúng thao tác chuẩn bị được thực thi, nên nó mang tính tường minh cao hơn. Thể hiện Command có thể được truyền trực tiếp vào một phương thức của Application Service:

```java
public class TenantIdentityService {
    ...
    @Transactional
    public String provisionTenant(ProvisionTenantCommand aCommand) {
        ...
        return tenant.tenantId().id();
    }
    ...
}

```

Bên cạnh cách tiếp cận phân phối (dispatching) tới một phương thức API của Application Service này, đúng như mô tả của pattern, chúng ta hoàn toàn có thể thay thế hoặc bổ sung bằng việc gửi các Command vào một hàng đợi để được điều phối tới một Command Handler. Hãy xem một Command Handler có ngữ nghĩa tương đương với một phương thức của Application Service, nhưng được tách rời về mặt thời gian (temporally decoupled). Như được thảo luận trong Phụ lục A, điều này mang lại thông lượng cao hơn và khả năng mở rộng tốt hơn cho việc xử lý Command.

## Decoupled Service Output

Đôi ba lần trước đó, tôi đã thảo luận về việc sử dụng Data Transformer như một giải pháp để đáp ứng các loại client khác nhau với kiểu dữ liệu cụ thể mà chúng yêu cầu. Cách tiếp cận đó dùng các Transformer để sinh ra dữ liệu dưới một kiểu cụ thể vốn triển khai một interface trừu tượng dùng chung cho tất cả các kiểu liên quan. Một lần nữa, từ góc nhìn của client, nó có thể trông giống như sau:

```java
TenantData tenantData =
    tenantIdentityService.provisionTenant(
        ...,
        myTenantDataTransformer);

TenantPresentationModel tenantPresentationModel =
    new TenantPresentationModel(tenantData.value());

```

Các Application Service được thiết kế như một API, có cả đầu vào và đầu ra. Lý do truyền vào một Data Transformer là để tạo ra kiểu đầu ra cụ thể mà client cần.

Sẽ ra sao nếu chúng ta chọn một hướng đi hoàn toàn khác và đặt ra quy tắc rằng các Application Service luôn được khai báo trả về `void`, và do đó, không bao giờ trực tiếp trả lại dữ liệu cho client? Cơ chế đó sẽ hoạt động như thế nào? Câu trả lời nằm ở tư duy mà Hexagonal Architecture (4) (kiến trúc lục giác) đề xướng: việc sử dụng phong cách Ports and Adapters (cổng và bộ tiếp hợp). Trong trường hợp này, chúng ta sẽ sử dụng một Port đầu ra tiêu chuẩn duy nhất cùng với bất kỳ số lượng adapter nào, mỗi adapter dành riêng cho một loại client. Làm như vậy sẽ mang lại một phương thức Application Service `provisionTenant()` tương tự như sau:

```java
public class TenantIdentityService {
    ...
    @Transactional
    @PreAuthorize("hasRole('SubscriberRepresentative')")
    public void provisionTenant(
        String aTenantName,
        String aTenantDescription,
        boolean isActive,
        FullName anAdministratorName,
        EmailAddress anEmailAddress,
        PostalAddress aPostalAddress,
        Telephone aPrimaryTelephone,
        Telephone aSecondaryTelephone,
        String aTimeZone) {
        Tenant tenant = this
            .tenantProvisioningService
            .provisionTenant(
                aTenantName,
                aTenantDescription,
                isActive,
                anAdministratorName,
                anEmailAddress,
                aPostalAddress,
                aPrimaryTelephone,
                aSecondaryTelephone,
                aTimeZone);
        this.tenantIdentityOutputPort().write(tenant);
    }
    ...
}

```

Port đầu ra ở đây là một Port được đặt tên cụ thể nằm ở biên của ứng dụng. Khi sử dụng Spring, nó sẽ là một bean được tiêm vào trong dịch vụ. Điều duy nhất mà `provisionTenant()` cần biết là nó phải gọi `write()` vào Port thể hiện `Tenant` mà nó nhận được từ Domain Service. Port này sẽ có nhiều reader (bộ đọc), các reader này tự đăng ký trước khi sử dụng Application Service. Khi thao tác `write()` diễn ra, từng reader đã đăng ký sẽ nhận tín hiệu để đọc dữ liệu đầu ra này làm dữ liệu đầu vào của mình. Tại thời điểm đó, các reader có thể chuyển đổi dữ liệu đầu ra bằng cơ chế đã được thiết lập, chẳng hạn như một Data Transformer.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000583_6a541b0353c8a1f050501a8bc6ce87f4bab59933db71c25fb31d5bdef4c4c5ad.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000584_6c85145667f90dabc83278c0a89c2501800eb29072136ebab0c81f8b9b220128.png)

Đây không phải là một sự ngụy tạo cầu kỳ nhằm thêm thắt độ phức tạp vào kiến trúc của bạn. Sức mạnh của nó cũng giống như bất kỳ kiến trúc Ports and Adapters nào khác, cho dù là dành cho hệ thống phần mềm hay thiết bị phần cứng. Mỗi thành phần chỉ cần hiểu dữ liệu đầu vào mà nó đọc, hành vi nội tại của chính nó, và Port mà nó ghi dữ liệu đầu ra.

Việc ghi vào một Port về cơ bản khá tương đồng với những gì một phương thức command thuần túy của Aggregate thực hiện khi nó không tạo ra giá trị trả về, nhưng nó lại phát đi một Domain Event (8) (sự kiện miền). Trong trường hợp của Aggregate, bộ phát Domain Event Publisher (8) đóng vai trò là một Port đầu ra của Aggregate. Xa hơn nữa, nếu chúng ta giải quyết bài toán truy vấn trạng thái của một Aggregate bằng cách sử dụng Double-Dispatch trên một Mediator, thì cách làm đó cũng tương tự như việc áp dụng Ports and Adapters.

Một nhược điểm của cách tiếp cận Ports and Adapters là nó có thể khiến việc đặt tên cho các phương thức truy vấn của Application Service trở nên khó khăn hơn. Hãy xem xét phương thức `tenant()` từ dịch vụ mẫu. Tên gọi đó giờ đây dường như không còn thích hợp nữa bởi vì nó không còn trả về đối tượng `Tenant` mà nó truy vấn. Tên gọi `provisionTenant()` vẫn hoạt động tốt cho API cấp phát vì trên thực tế nó đã trở thành một phương thức command thuần túy, không còn trả về giá trị. Nhưng chúng ta có thể muốn nghĩ ra một cái tên phù hợp hơn cho `tenant()`. Cách xử lý sau đây có thể cải thiện tình hình đôi chút:

```java
...
@Override
@Transactional(readOnly = true)
public void findTenant(TenantId aTenantId) {
    Tenant tenant = this
        .tenantRepository
        .tenantOfId(aTenantId);
    this.tenantIdentityOutputPort().write(tenant);
}
...
}

```

Cái tên `findTenant()` có thể sẽ phù hợp vì từ "tìm kiếm" không nhất thiết hàm ý phải trả về kết quả ngay tại chỗ. Bất kể tên nào được chọn, tình huống này cũng khẳng định một điều rằng mỗi quyết định kiến trúc chúng ta đưa ra đều mang lại cả những hệ quả tích cực lẫn tiêu cực.

## Composing Multiple Bounded Contexts

Các ví dụ mà tôi đã cung cấp chưa đề cập đến khả năng một giao diện người dùng đơn lẻ có thể cần phải kết hợp từ hai hay nhiều mô hình miền. Trong các ví dụ của tôi, các khái niệm từ các mô hình thượng nguồn (upstream model) được tích hợp vào các mô hình hạ nguồn (downstream model) bằng cách dịch chúng sang các thuật ngữ của mô hình hạ nguồn.

Điều đó khác với nhu cầu kết hợp nhiều mô hình thành một thể hiển thị hợp nhất duy nhất, như được thể hiện trong Hình 14.3. Các mô hình bên ngoài, trong ví dụ này, là Products Context, Discussions Context, và Reviews Context. Giao diện người dùng không nên nhận biết rằng nó đang kết hợp nhiều mô hình. Khi một tình huống tương tự diễn ra trong ứng dụng của bạn, bạn nên suy nghĩ về cách mà cấu trúc và cách đặt tên Module (9) hỗ trợ cho nhu cầu của bạn, cũng như cách mà các Application Service có thể làm mịn sự đứt gãy tiềm tàng giữa các mô hình khác nhau.

Một giải pháp là sử dụng nhiều Application Layer, không giống như những gì hiển thị trong Hình 14.3. Với nhiều Application Layer, bạn sẽ cần cung cấp các thành phần giao diện người dùng độc lập đi kèm với từng tầng, trong đó các thành phần giao diện người dùng sẽ có mối liên hệ mật thiết với một mô hình miền cụ thể ở phía dưới. Đây về cơ bản là phong cách portal-portlet. Dẫu vậy, sẽ khó khăn hơn để làm cho các Application Layer riêng rẽ cùng các thành phần UI độc lập hòa hợp đồng điệu theo các luồng use case — vốn là điều mà giao diện người dùng quan tâm.

Vì Application Layer quản lý các use case, nên cách dễ nhất có thể là tạo ra một Application Layer duy nhất đóng vai trò là nơi thực tế để kết hợp mô hình, đây chính là cách tiếp cận được minh họa trong Hình 14.3. Các dịch vụ trong tầng duy nhất đó hoàn toàn không chứa business domain logic. Nó sẽ chỉ phục vụ việc gom các đối tượng từ từng mô hình lại thành các đối tượng gắn kết mà giao diện người dùng cần. Rất có thể trong trường hợp này, bạn sẽ

Hình 14.3 Có những thời điểm một UI phải kết hợp nhiều mô hình. Ở đây ba mô hình được kết hợp bằng cách sử dụng một Application Layer duy nhất.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000585_c97652607ef3d8c79cdc089afe9f0c2081066e88b961b34bfef509b95d510b34.png)

531

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000586_121b39b3bc3d2713bb6029f4a9749aa3da1200b628648c4924e3c4e5ad2f12cc.png)

đặt tên các Module trong User Interface và Application Layer theo mục đích của sự kết hợp này, thành một ngữ cảnh có tên cụ thể:

```
com.consumerhive.productreviews.presentation
com.consumerhive.productreviews.application

```

Consumer Hive cung cấp tính năng thảo luận và đánh giá sản phẩm tiêu dùng. Ứng dụng này đã tách biệt Products Context khỏi Discussions Context và Reviews Context. Dẫu vậy, các Module ở tầng presentation và application lại phản ánh sự thống nhất dưới một giao diện người dùng duy nhất. Rất có thể nó lấy danh mục sản phẩm từ một hoặc nhiều nguồn bên ngoài, trong khi các phần thảo luận và đánh giá lại chính là Core Domain (miền lõi) của nó.

Và khi nói về Core Domain . . . Thật kỳ lạ, bạn nhận thấy điều gì ở đây? Chẳng phải Application Layer này thực chất đang đóng vai trò như một mô hình miền mới đi kèm một Anticorruption Layer (3) (lớp chống suy thoái) tích hợp sẵn hay sao? Đúng vậy, về cơ bản nó là một Bounded Context mới thuộc dạng "chắp vá giá rẻ" (bargain-basement). Tại đây, các Application Service quản lý việc hợp nhất nhiều DTO khác nhau, mô phỏng lại một dạng Anemic Domain Model (1) (mô hình miền thiếu máu). Nó mang hơi hướng của một cách tiếp cận Transaction Script (1) (kịch bản giao dịch) dùng để mô hình hóa Core Domain.

Nếu bạn quyết định rằng sự kết hợp ba mô hình của Consumer Hive đang tha thiết đòi hỏi một Domain Model (1) mới dưới dạng một mô hình đối tượng hợp nhất trong một Bounded Context duy nhất, bạn có thể đặt tên cho các Module của mô hình mới như sau:

```
com.consumerhive.productreviews.domain.model.product
com.consumerhive.productreviews.domain.model.discussion
com.consumerhive.productreviews.domain.model.review

```

Sau cùng, bạn sẽ phải quyết định cách mô hình hóa tình huống này. Liệu bạn có quyết định sử dụng thiết kế chiến lược (strategic design) và thậm chí cả thiết kế chiến thuật (tactical design) để tạo ra một mô hình mới hay không? Ở mức tối thiểu, tình huống này đặt ra câu hỏi: Đâu là ranh giới giữa việc kết hợp nhiều Bounded Context vào một giao diện người dùng duy nhất, và việc tạo ra một Bounded Context mới, tinh gọn với một mô hình miền hợp nhất? Mỗi trường hợp đều phải được cân nhắc kỹ lưỡng. Một hệ thống ít quan trọng hơn sẽ có những yếu tố tác động và ưu tiên khác. Dù vậy, chúng ta không được phép đưa ra những quyết định như vậy một cách tùy tiện. Cần xem xét cẩn trọng các tiêu chí đã được nêu ra trong phần Bounded Context. Rốt cuộc, cách tiếp cận tốt nhất chính là cách mang lại nhiều lợi ích nhất cho nghiệp vụ kinh doanh.

## Infrastructure

Nhiệm vụ của tầng Infrastructure (hạ tầng) là cung cấp các khả năng kỹ thuật cho các phần khác của ứng dụng. Dù tránh đi sâu vào cuộc thảo luận về Layers (4), việc duy trì tư duy theo DIP (Dependency Inversion Principle - nguyên lý đảo ngược phụ thuộc) vẫn luôn rất hữu ích. Vì vậy, cho dù tầng hạ tầng của bạn nằm ở đâu về mặt kiến trúc, hệ thống sẽ vận hành rất trơn tru nếu các thành phần của nó phụ thuộc vào các interface từ giao diện người dùng, Application Service, và mô hình miền vốn đòi hỏi các khả năng kỹ thuật đặc biệt. Bằng cách đó, khi một Application Service tra cứu một Repository, nó sẽ chỉ phụ thuộc duy nhất vào interface từ mô hình miền, nhưng lại sử dụng lớp triển khai từ hạ tầng. Hình 14.4 cung cấp biểu đồ cấu trúc tĩnh UML để minh họa cách cơ chế này hoạt động.

Hình 14.4 Application Service phụ thuộc vào interface Repository từ mô hình miền nhưng sử dụng class triển khai từ hạ tầng. Các package đóng gói những trách nhiệm trên diện rộng.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000587_8178be62f88d7f60e8ca7f404ca4b79c7c75a100f9f2d254251cfd489da6a785.png)

Việc tra cứu có thể diễn ra ngầm định thông qua Dependency Injection [Fowler, DI] hoặc sử dụng một Service Factory (nhà máy dịch vụ). Phần cuối của chương này, 'Enterprise Component Containers,' sẽ thảo luận về các tùy chọn này. Lặp lại một phần của Application Service được dùng làm ví dụ xuyên suốt, bạn có thể thấy lại ở đây cách mà Service Factory được dùng để tra cứu Repository:

```java
package com.saasovation.identityaccess.application;

```

```java
public class TenantIdentityService {
    ...
    @Override
    @Transactional(readOnly = true)
    public Tenant tenant(TenantId aTenantId) {
        Tenant tenant = DomainRegistry
            .tenantRepository()
            .tenantOfId(aTenantId);

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000588_ffe6c9773b73f2add2edb82305a5572f54d33fa79bed14ce518f876a1b8a446b.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000589_5078b7c8e273d7df483d194bda1a538df44ea0102a80d16ae8620bf6c7dc3983.png)

```java
        return tenant;
    }
    ...
}

```

Application Service này thay vào đó cũng có thể đã được tiêm Repository, hoặc chúng ta có thể thiết lập các phụ thuộc đầu vào thông qua các tham số của constructor.

Các bản triển khai của Repository được giữ trong tầng hạ tầng vì chúng xử lý việc lưu trữ — đây không phải là trách nhiệm mà mô hình nên gánh vác. Bạn sẽ sử dụng hạ tầng để triển khai các interface đòi hỏi việc dùng messaging, chẳng hạn như hàng đợi thông điệp (message queue) và email. Nếu có các thành phần giao diện người dùng đặc biệt xử lý việc sinh biểu đồ đồ họa, bản đồ và những thứ tương tự, chúng cũng sẽ được triển khai ở tầng hạ tầng.

## Enterprise Component Containers

Ngày nay, các máy chủ ứng dụng doanh nghiệp (enterprise application server) đã trở thành một loại hàng hóa phổ thông. Dường như có rất ít sự đổi mới đột phá ở chính các máy chủ này cũng như trong các component container chạy bên trong chúng. Chúng ta có thể sử dụng Enterprise JavaBeans (EJB) làm Session Facade [Crupi et al.] hoặc các JavaBean đơn giản được quản lý bởi các container đảo ngược điều khiển (IoC container) như Spring để tạo thuận lợi cho việc sử dụng các Application Service. Đã có nhiều tranh luận về việc giải pháp nào tốt hơn, nhưng cũng đã có rất nhiều sự hội tụ giữa các framework. Trên thực tế, khi nhìn sâu vào bên trong một số máy chủ JEE, người ta phát hiện ra rằng một vài máy chủ trong số đó được triển khai bằng chính Spring.

## Is It WebLogic or Spring?

Nếu bạn xem một stack trace từ Oracle WebLogic Server, rất có thể bạn sẽ thấy các tham chiếu đến các class thuộc Spring Framework. Chúng không phải là một phần trong gói triển khai ứng dụng của bạn. Trong trường hợp này, bạn chỉ đang sử dụng JEE tiêu chuẩn với các EJB Session Bean. Các class Spring mà bạn đang thấy thực chất là một phần trong bản triển khai EJB container của WebLogic. Phải chăng đây là trường hợp 'nếu không thể đánh bại họ, hãy gia nhập cùng họ'?

Tôi đã chọn triển khai ba Bounded Context mẫu mà tôi cung cấp bằng cách sử dụng Spring Framework. Dù vậy, những ví dụ này hoàn toàn có thể dễ dàng chuyển đổi sang các nền tảng enterprise container khác. Do đó, bạn không bị mất mát gì nếu dự án của bạn không dùng Spring, và bạn vẫn hoàn toàn có thể cảm thấy thoải mái khi đọc qua các ví dụ. Sự khác biệt về mặt logic giữa các container khác nhau là rất nhỏ.

Trong Repositories (12) có trình bày cấu hình Spring dùng để kết nối (wire up) hỗ trợ transaction cho các Application Service phục vụ việc lưu trữ bền vững các đối tượng miền. Ở đây, hãy cùng xem xét các phần khác của cấu hình Spring. Hai file đáng chú ý là:

```
config/spring/applicationContext-application.xml
config/spring/applicationContext-domain.xml

```

Đúng như tên file đã chỉ rõ, các Application Service và các thành phần của mô hình miền được kết nối bên trong các file này. Hãy xem xét một vài cấu hình từ file kết nối tầng ứng dụng:

```xml
<beans ...>
    <aop:aspectj-autoproxy/>
    <tx:annotation-driven transaction-manager="transactionManager"/>
    ...
    <bean id="applicationServiceRegistry"
          class="com.saasovation.identityaccess.application.ApplicationServiceRegistry"
          autowire="byName">
    </bean>
    ...
    <bean id="tenantIdentityService"
          class="com.saasovation.identityaccess.application.TenantIdentityService"
          autowire="byName">
    </bean>
    ...
</beans>

```

Bean `tenantIdentityService` chính là bean đã được xem xét trước đó. Bean này có thể được nối kết vào các bean Spring khác, chẳng hạn như ở giao diện người dùng. Nếu bạn thích một Service Factory hơn là việc tiêm các thể hiện bean vào nhau, chúng ta có thể dùng bean còn lại trong cấu hình là `applicationServiceRegistry`. Bean này cung cấp khả năng tra cứu để truy cập vào tất cả các Application Service. Bạn sẽ sử dụng nó như sau:

```java
...
ApplicationServiceRegistry
    .tenantIdentityService()
    .deactivateTenant(tenantId);

```

Chúng ta có thể làm như vậy bởi vì bản thân nó đã được tiêm `ApplicationContext` của Spring ngay khi bean được tạo mới.

Một loại registry bean tương tự cũng được cung cấp để truy cập vào các thành phần của mô hình miền, chẳng hạn như các Repository và Domain Service. Dưới đây là cấu hình bean cho Registry, Repository và Domain Service của mô hình miền:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000590_870e36d1131aa2e69f054735df693c29fc79378ad16571ce6f5dfa0d51ba649f.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000591_c0791247533eb60d1078b0027fe801dd04493c8678035771e1e686f92d12c45f.png)

```xml
<beans ...>
    ...
    <bean id="authenticationService"
          class="com.saasovation.identityaccess.infrastructure.services.DefaultEncryptionAuthenticationService"
          autowire="byName">
    </bean>
    <bean id="domainRegistry"
          class="com.saasovation.identityaccess.domain.model.DomainRegistry"
          autowire="byName">
    </bean>
    <bean id="encryptionService"
          class="com.saasovation.identityaccess.infrastructure.services.MessageDigestEncryptionService"
          autowire="byName">
    </bean>
    <bean id="groupRepository"
          class="com.saasovation.identityaccess.infrastructure.persistence.HibernateGroupRepository"
          autowire="byName">
    </bean>
    <bean id="roleRepository"
          class="com.saasovation.identityaccess.infrastructure.persistence.HibernateRoleRepository"
          autowire="byName">
    </bean>
    <bean id="tenantProvisioningService"
          class="com.saasovation.identityaccess.domain.model.identity.TenantProvisioningService"
          autowire="byName">
    </bean>
    <bean id="tenantRepository"
          class="com.saasovation.identityaccess.infrastructure.persistence.HibernateTenantRepository"
          autowire="byName">
    </bean>

```

```xml
    <bean id="userRepository"
          class="com.saasovation.identityaccess.infrastructure.persistence.HibernateUserRepository"
          autowire="byName">
    </bean>
</beans>

```

Bằng cách sử dụng `DomainRegistry`, chúng ta có thể truy cập vào bất kỳ bean nào trong số các bean đã được đăng ký này của Spring. Tất cả các bean cũng đều sẵn sàng để được tiêm phụ thuộc vào các bean Spring khác. Như vậy, các Application Service có thể chọn sử dụng Service Factory hoặc Dependency Injection. Hãy xem phần Services (7) để có cuộc thảo luận chuyên sâu hơn về việc sử dụng hai cách tiếp cận này so với thiết lập phụ thuộc dựa trên constructor.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000592_0d9f6ec47c8ff53e2f858123a8efe6c992bf27c96898845ef00a82c2b0f2c31e.png)

## Wrap-Up

Trong chương này, chúng ta đã tìm hiểu cách thức ứng dụng hoạt động bên ngoài mô hình miền.

* Bạn đã xem xét một số kỹ thuật để render dữ liệu của mô hình lên các giao diện người dùng.
* Bạn đã thấy các cách tiếp nhận dữ liệu đầu vào của người dùng để áp dụng vào mô hình miền.
* Bạn đã học được nhiều tùy chọn đa dạng để truyền tải dữ liệu của mô hình, ngay cả khi có thể có rất nhiều loại giao diện người dùng khác nhau.
* Bạn đã tìm hiểu sâu về các Application Service và những gì chúng chịu trách nhiệm.
* Bạn đã được giới thiệu một tùy chọn để phân tách đầu ra khỏi các loại client cụ thể.
* Bạn đã học được những cách sử dụng tầng hạ tầng để tách rời các phần triển khai kỹ thuật ra khỏi mô hình miền.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000593_96181ade65db01f8f753a8f22462aa64173e9a807024c804cb44db87e704a3f3.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000594_9d733b2da579f3f9a927812ddd1bba5242f52f4c5134cc27886ac79a2ce95077.png)

* Bạn đã xem xét cách áp dụng DIP để làm cho các client ở mọi khía cạnh của ứng dụng đều phụ thuộc vào các trừu tượng thay vì các chi tiết triển khai, giúp thúc đẩy tính liên kết lỏng.
* Cuối cùng, bạn đã thấy cách mà các máy chủ ứng dụng phổ thông và các enterprise component container có thể tiếp thêm sức mạnh vận hành thực tế cho các ứng dụng của bạn (give legs to your applications).

> 💡 **Giải thích thêm:** Thành ngữ tiếng Anh "give legs to [something]" (nghĩa đen: "gắn thêm đôi chân cho...") có nghĩa là tiếp thêm khả năng vận hành thực tế, sự bền bỉ và sức sống để hệ thống có thể tự đứng vững, mở rộng quy mô và chạy ổn định trong môi trường doanh nghiệp thực tế (production).
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Giờ đây, bạn đã có một nền tảng vững chắc để triển khai DDD từ mô hình miền được chăm chút kỹ lưỡng cho đến các thành phần của toàn bộ ứng dụng.

## Appendix A

## Aggregates and Event Sourcing: A+ES

## Contributed by Rinat Abdullin

Khái niệm Event Sourcing (nguồn sự kiện / kiến trúc lưu vết sự kiện) đã được sử dụng trong nhiều thập kỷ, nhưng gần đây đã được Greg Young phổ biến rộng rãi hơn nhờ việc áp dụng nó vào DDD [Young, ES].

Event Sourcing có thể được dùng để biểu diễn toàn bộ trạng thái của một Aggregate (10) dưới dạng một chuỗi các Event (8) (sự kiện) đã xảy ra kể từ thời điểm nó được tạo. Các Event này được dùng để tái tạo lại trạng thái của Aggregate bằng cách phát lại (replay) chúng theo đúng thứ tự mà chúng đã diễn ra. Tiền đề ở đây là cách tiếp cận này sẽ đơn giản hóa việc lưu trữ dữ liệu bền vững và cho phép nắm bắt trọn vẹn các khái niệm có các thuộc tính hành vi phức tạp.

Tập hợp các Event đại diện cho trạng thái của từng Aggregate được lưu lại trong một Event Stream (luồng sự kiện) chỉ cho phép ghi thêm (append-only). Trạng thái của Aggregate này sẽ tiếp tục biến đổi qua các thao tác kế tiếp bằng cách nối thêm các Event mới vào cuối Event Stream, như được minh họa trong Hình A.1. (Trong phụ lục này, các Event được thể hiện dưới dạng các hình chữ nhật màu xám nhạt để giúp chúng nổi bật hơn so với các khái niệm khác.)

Event Stream của mỗi Aggregate thường được lưu trữ bền vững trong các Event Store (8) (kho lưu trữ sự kiện), nơi chúng được phân biệt duy nhất, thông thường là dựa theo danh tính (identity) của Entity (5) (thực thể) gốc. Cách xây dựng một Event Store chuyên biệt dùng cho Event Sourcing sẽ được đề cập chi tiết hơn ở phần sau của phụ lục này.

Kể từ đây trở đi, chúng ta hãy gọi cách tiếp cận sử dụng Event Sourcing để duy trì trạng thái của các Aggregate và lưu trữ bền vững chúng là A+ES.

Một số lợi ích chính của A+ES là:

* Event Sourcing đảm bảo rằng lý do đằng sau mỗi thay đổi đối với một thể hiện Aggregate sẽ không bao giờ bị mất đi. Khi sử dụng cách tiếp cận truyền thống là

Hình A.1 Một Event Stream chứa các Domain Event theo thứ tự xảy ra

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000595_bccd4b99bab0f4e986bfc210f14faf8c3a511752400f32c016a0e1444ae3fa9c.png)